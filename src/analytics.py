import pandas as pd
import numpy as np

REQUIRED = ["date", "invoice_id", "supplier", "department", "category", "quantity", "unit_price", "amount", "approval_status"]

def prepare_data(df):
    out = df.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    missing = [c for c in REQUIRED if c not in out.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for c in ["quantity", "unit_price", "amount"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["date", "amount", "supplier"]).copy()
    out["amount"] = out["amount"].clip(lower=0)
    out["month"] = out["date"].dt.to_period("M").astype(str)
    out["unit_price"] = out["unit_price"].fillna(out["amount"] / out["quantity"].replace(0, np.nan))
    out["approval_status"] = out["approval_status"].fillna("Unknown").astype(str)
    return out

def detect_risks(df):
    d = df.copy()
    # Robust price anomaly score within category, with global fallback.
    group = d.groupby("category")["unit_price"]
    med = group.transform("median")
    mad = group.transform(lambda x: np.median(np.abs(x - np.median(x))) or 1.0)
    d["price_robust_z"] = 0.6745 * (d["unit_price"] - med) / mad.replace(0, 1)
    d["price_anomaly"] = d["price_robust_z"].abs() >= 3.5
    d["duplicate_invoice"] = d.duplicated("invoice_id", keep=False)
    d["policy_exception"] = d["approval_status"].str.lower().str.contains("off-policy|unauthorized|exception", regex=True)
    d["risk_score"] = (
        d["price_anomaly"].astype(int) * 35
        + d["duplicate_invoice"].astype(int) * 40
        + d["policy_exception"].astype(int) * 30
        + (d["amount"] > d["amount"].quantile(.95)).astype(int) * 10
    ).clip(0, 100)
    d["risk_level"] = pd.cut(d["risk_score"], [-1, 0, 34, 64, 100], labels=["Low", "Guarded", "High", "Critical"])
    return d

def supplier_scorecard(df):
    g = df.groupby("supplier", dropna=False).agg(
        spend=("amount","sum"), transactions=("po_id","count") if "po_id" in df else ("amount","size"),
        avg_unit_price=("unit_price","mean"), avg_reliability=("supplier_reliability","mean") if "supplier_reliability" in df else ("amount","mean"),
        flagged=("risk_score", lambda x: int((x >= 35).sum()))
    ).reset_index()
    g["risk_rate_pct"] = (g["flagged"] / g["transactions"].clip(lower=1) * 100).round(1)
    # Higher score is better; transparent heuristic, not a validated credit score.
    reliability = g["avg_reliability"].fillna(.8).clip(0,1)
    risk_penalty = (g["risk_rate_pct"].fillna(0) / 100).clip(0,1)
    g["supplier_health_score"] = ((reliability * 75) + ((1-risk_penalty) * 25)).round(1)
    return g.sort_values("spend", ascending=False)

def monthly_forecast(df, periods=6):
    monthly = df.groupby(pd.Grouper(key="date", freq="MS"))["amount"].sum().asfreq("MS", fill_value=0)
    if len(monthly) == 0:
        return pd.DataFrame(columns=["month","actual_or_forecast","series"])
    # Transparent seasonal-naive/trend blend; intentionally avoids pretending to be a production forecast.
    vals = monthly.values.astype(float)
    recent = vals[-min(6, len(vals)):]
    baseline = float(np.mean(recent)) if len(recent) else 0
    trend = float(np.mean(np.diff(recent))) if len(recent) > 1 else 0
    future_dates = pd.date_range(monthly.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    forecast = [max(0, baseline + trend * (i+1) * .35) for i in range(periods)]
    hist = pd.DataFrame({"month": monthly.index, "amount": vals, "series":"Historical"})
    fut = pd.DataFrame({"month": future_dates, "amount": forecast, "series":"Forecast"})
    return pd.concat([hist, fut], ignore_index=True)

def optimization_candidates(df):
    s = supplier_scorecard(df)
    if s.empty:
        return s
    # Rank supplier options using spend-weighted observed price and reliability.
    s["price_index"] = s["avg_unit_price"] / max(float(s["avg_unit_price"].median()), 1e-9)
    s["recommendation_score"] = (
        (s["supplier_health_score"] * .65) + ((1 / s["price_index"].clip(lower=.25, upper=4)) * 35)
    ).round(1)
    s["recommendation"] = np.where(s["recommendation_score"] >= 75, "Preferred candidate",
                            np.where(s["recommendation_score"] >= 60, "Review for sourcing", "Monitor"))
    return s.sort_values("recommendation_score", ascending=False)
