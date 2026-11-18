import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from src.analytics import prepare_data, detect_risks, supplier_scorecard, monthly_forecast, optimization_candidates

st.set_page_config(page_title="ProcureIQ AI | Procurement Intelligence", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

# Distinctive editorial palette: warm ivory, aubergine, coral, jade and lilac.
INK, CORAL, JADE, PLUM, CREAM = "#34233D", "#E45B35", "#2F9C85", "#8D5CC7", "#F7F3EE"
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background: #F7F3EE;}
[data-testid="stSidebar"] {background: #34233D;}
[data-testid="stSidebar"] * {color:#FFF9F3 !important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:7px 10px;border-radius:9px;}
h1,h2,h3 {font-family:'Manrope',sans-serif;color:#34233D;}
.hero {background:linear-gradient(115deg,#34233D 0%,#56364F 58%,#2F766B 100%);padding:28px 32px;border-radius:20px;color:#FFF9F3;margin:6px 0 22px 0;box-shadow:0 12px 28px rgba(52,35,61,.12);}
.hero h1 {color:#FFF9F3;font-size:34px;margin:0 0 6px 0;}
.hero p {color:#F8E9E1;margin:0;font-size:14px;}
.eyebrow {letter-spacing:2px;text-transform:uppercase;font-size:10px;font-weight:700;color:#F6B49C;}
.metric {background:#FFFCF8;border:1px solid #E9DED5;border-radius:15px;padding:15px 17px;min-height:102px;}
.metric .k {color:#786B79;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:700;}
.metric .v {color:#34233D;font-size:27px;font-weight:800;font-family:Manrope,sans-serif;margin-top:4px;}
.metric .s {color:#2F9C85;font-size:11px;margin-top:2px;}
.section {border-left:4px solid #E45B35;padding-left:12px;margin:22px 0 12px 0;}
.note {background:#F0E8F3;border-radius:12px;padding:12px 15px;color:#513B5B;font-size:13px;}
.footer {border-top:1px solid #E4D9D1;margin-top:38px;padding:18px 0 8px 0;color:#766A78;font-size:12px;text-align:center;}
div[data-testid="stDataFrame"] {border:1px solid #E8DED6;border-radius:12px;overflow:hidden;}
.stButton>button {background:#E45B35;color:white;border:0;border-radius:10px;font-weight:700;}
.stDownloadButton>button {border-radius:10px;border:1px solid #2F9C85;color:#236D60;}

/* FILE UPLOADER - IMPROVED CONTRAST */

[data-testid="stFileUploader"] {
    background: #FFF9F3 !important;
    border: 1px solid #DCCBC0 !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

[data-testid="stFileUploader"] section {
    background: #FFF9F3 !important;
    border: 1px dashed #C7A99A !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploader"] section * {
    color: #34233D !important;
}

[data-testid="stFileUploader"] button {
    background: #E45B35 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] small {
    color: #786B79 !important;
}

[data-testid="stFileUploader"] svg {
    fill: #E45B35 !important;
}

</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample():
    return pd.read_csv(ROOT / "sample_data" / "procurement_transactions.csv")

def money(x):
    return f"₹{x:,.0f}"

with st.sidebar:
    st.image(str(ROOT / "assets" / "procureiq_logo.svg"), width=105)
    st.markdown("## ProcureIQ AI")
    st.caption("PROCUREMENT INTELLIGENCE")
    st.markdown("---")
    st.markdown("**DATA SOURCE**")
    uploaded = st.file_uploader("Upload procurement CSV", type=["csv"])
    st.caption("Use the included sample dataset to explore all modules.")
    st.markdown("---")
    st.caption("Demo environment • Synthetic data")

try:
    raw = pd.read_csv(uploaded) if uploaded else load_sample()
    base = prepare_data(raw)
    data = detect_risks(base)
except Exception as e:
    st.error(f"Could not load this dataset: {e}")
    st.info("Required columns: date, invoice_id, supplier, department, category, quantity, unit_price, amount, approval_status.")
    st.stop()

# CENTERED WORKSPACE NAVIGATION
st.markdown("""
<style>
div[data-testid="stRadio"] > div {
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
}

div[data-testid="stRadio"] label {
    background: #FFFFFF;
    border: 1px solid #E5D9D0;
    border-radius: 10px;
    padding: 9px 15px;
    transition: all 0.2s ease;
}

div[data-testid="stRadio"] label:hover {
    border-color: #E45B35;
    background: #FFF0E9;
}


/* PROCUREIQ - CENTERED PREMIUM NAVIGATION */

div[data-testid="stRadio"] {
    width: 100% !important;
    margin: 22px auto 30px auto !important;
    display: flex !important;
    justify-content: center !important;
}

div[data-testid="stRadio"] > div {
    width: 100% !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] {
    width: 100% !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 12px !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label {
    flex: 0 0 auto !important;
    margin: 0 !important;
    white-space: nowrap !important;
}


</style>
""", unsafe_allow_html=True)

total_spend = float(data["amount"].sum())
flagged = int((data["risk_score"] >= 35).sum())
dup = int(data["duplicate_invoice"].sum())
policy = int(data["policy_exception"].sum())
supplier_count = int(data["supplier"].nunique())

# Maintain selected workspace before rendering the hero
page = st.session_state.get(
    "procureiq_workspace_navigation",
    "Executive Command"
)

st.markdown(f"""
<div class="hero">
 <div class="eyebrow">PROCUREMENT • RISK • PERFORMANCE</div>
 <h1>{page}</h1>
 <p>Turn fragmented purchasing data into controlled spend, resilient sourcing and confident decisions.</p>
</div>
""", unsafe_allow_html=True)


# PREMIUM WORKSPACE NAVIGATION

st.markdown("""
<style>

/* Navigation container */
div[data-testid="stRadio"] {
    background: #FFFFFF;
    border: 1px solid #E9DED5;
    border-radius: 15px;
    padding: 12px 15px;
    margin: 12px auto 28px auto;
    box-shadow: 0 4px 16px rgba(52,35,61,0.045);
}

/* Hide radio group heading */
div[data-testid="stRadio"] > label {
    display: none;
}

/* Single-row workspace layout */
div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    gap: 12px !important;
    margin: 0 auto !important;
}

/* Hide radio circles */
div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Workspace buttons */
div[data-testid="stRadio"] div[role="radiogroup"] label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 10px 13px;
    white-space: nowrap;
    transition: all 0.2s ease;
    color: #786B79;
    font-size: 12px;
    font-weight: 600;
}

/* Hover */
div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background: #FFF1EB;
    border-color: #F0C5B5;
    color: #C84F31;
}

/* Active workspace */
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background: #34233D;
    color: #FFFFFF !important;
    border-color: #34233D;
    box-shadow: 0 3px 9px rgba(52,35,61,0.16);
}

/* Active text */
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
    color: #FFFFFF !important;
}

/* Remove unnecessary widget spacing */
div[data-testid="stRadio"] {
    width: 100%;
    margin: 20px auto 28px auto;
    text-align: center;
    gap: 0;
}

</style>
""", unsafe_allow_html=True)

page = st.radio(
    "WORKSPACES",
    [
        "Executive Command",
        "Spend Intelligence",
        "Invoice & Policy Audit",
        "Supplier Risk",
        "Cost Forecasting",
        "Sourcing Optimizer",
        "Data Studio"
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="procureiq_workspace_navigation"
)


def metric(label, value, sub="LIVE DATA"):
    st.markdown(f'<div class="metric"><div class="k">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>', unsafe_allow_html=True)

if page == "Executive Command":
    cols = st.columns(5)
    with cols[0]: metric("Total addressable spend", money(total_spend))
    with cols[1]: metric("Purchase records", f"{len(data):,}")
    with cols[2]: metric("Risk signals", f"{flagged:,}", "Needs review")
    with cols[3]: metric("Duplicate invoice rows", f"{dup:,}", "Invoice control")
    with cols[4]: metric("Active suppliers", f"{supplier_count:,}")
    st.markdown('<div class="section"><h3>Spend pulse & exposure</h3></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([1.45,1])
    with c1:
        m = data.groupby("month",as_index=False)["amount"].sum()
        fig = px.area(m,x="month",y="amount",title="Monthly procurement outflow",color_discrete_sequence=[CORAL])
        fig.update_traces(line_width=3,fillcolor="rgba(228,91,53,.16)")
        fig.update_layout(paper_bgcolor="#FFFCF8",plot_bgcolor="#FFFCF8",font_color=INK,margin=dict(l=10,r=10,t=48,b=10),yaxis_title="Spend (₹)",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        cat = data.groupby("category",as_index=False)["amount"].sum().sort_values("amount",ascending=False)
        fig = px.pie(cat,names="category",values="amount",hole=.62,color_discrete_sequence=[CORAL,JADE,PLUM,"#E8B44A","#6D8DA6","#D889A8","#A6A06A"],title="Spend mix by category")
        fig.update_layout(paper_bgcolor="#FFFCF8",font_color=INK,legend_title="",margin=dict(l=5,r=5,t=48,b=5))
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section"><h3>Priority attention queue</h3></div>', unsafe_allow_html=True)
    queue = data[data["risk_score"]>=35].sort_values("risk_score",ascending=False).head(12)
    st.dataframe(queue[["po_id","date","invoice_id","supplier","category","amount","approval_status","risk_score","risk_level"]],use_container_width=True,hide_index=True)
    st.markdown('<div class="note">Decision cue: prioritize high-value critical records first, then validate the source invoice, purchase order and approval trail before taking action.</div>',unsafe_allow_html=True)

elif page == "Spend Intelligence":
    a,b = st.columns(2)
    with a: dept = st.multiselect("Departments",sorted(data.department.unique()),default=sorted(data.department.unique()))
    with b: cats = st.multiselect("Categories",sorted(data.category.unique()),default=sorted(data.category.unique()))
    d = data[data.department.isin(dept)&data.category.isin(cats)]
    c1,c2,c3 = st.columns(3)
    with c1: metric("Filtered spend",money(d.amount.sum()))
    with c2: metric("Average purchase",money(d.amount.mean() if len(d) else 0))
    with c3: metric("Departments in view",str(d.department.nunique()))
    l,r=st.columns(2)
    with l:
        g=d.groupby("department",as_index=False).amount.sum().sort_values("amount",ascending=True)
        fig=px.bar(g,x="amount",y="department",orientation="h",title="Spend by department",color="amount",color_continuous_scale=["#F6C5B4",CORAL])
        fig.update_layout(paper_bgcolor="#FFFCF8",plot_bgcolor="#FFFCF8",font_color=INK,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    with r:
        g=d.groupby("supplier",as_index=False).amount.sum().nlargest(10,"amount")
        fig=px.treemap(g,path=["supplier"],values="amount",title="Top supplier concentration",color="amount",color_continuous_scale=["#B8DCD2",JADE])
        fig.update_layout(paper_bgcolor="#FFFCF8",font_color=INK)
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section"><h3>Category × department matrix</h3></div>',unsafe_allow_html=True)
    pivot=d.pivot_table(index="category",columns="department",values="amount",aggfunc="sum",fill_value=0)
    st.dataframe(pivot.style.format("₹{:,.0f}"),use_container_width=True)

elif page == "Invoice & Policy Audit":
    c1,c2,c3=st.columns(3)
    with c1: metric("Duplicate invoice rows",str(dup),"Same invoice ID appears more than once")
    with c2: metric("Off-policy purchases",str(policy),"Approval status exception")
    with c3: metric("High / critical signals",str(int((data.risk_score>=65).sum())),"Rule-based risk queue")
    st.markdown('<div class="section"><h3>Audit workbench</h3></div>',unsafe_allow_html=True)
    filter_choice=st.selectbox("Show records",["All flagged","Duplicate invoices","Policy exceptions","Price anomalies","High-value purchases"])
    if filter_choice=="Duplicate invoices": q=data[data.duplicate_invoice]
    elif filter_choice=="Policy exceptions": q=data[data.policy_exception]
    elif filter_choice=="Price anomalies": q=data[data.price_anomaly]
    elif filter_choice=="High-value purchases": q=data[data.amount>=data.amount.quantile(.95)]
    else: q=data[data.risk_score>=35]
    st.dataframe(q.sort_values("risk_score",ascending=False)[["po_id","date","invoice_id","supplier","department","amount","approval_status","duplicate_invoice","price_anomaly","policy_exception","risk_score"]],use_container_width=True,hide_index=True)
    st.download_button("Download audit queue CSV",q.to_csv(index=False).encode(), "procureiq_audit_queue.csv","text/csv")
    st.caption("Flags are screening signals, not proof of fraud or misconduct. Verify against source documents and policy.")

elif page == "Supplier Risk":
    score=supplier_scorecard(data)
    c1,c2=st.columns([1.2,1])
    with c1:
        fig=px.scatter(score,x="avg_reliability",y="risk_rate_pct",size="spend",color="supplier_health_score",hover_name="supplier",title="Supplier reliability vs flagged-record rate",color_continuous_scale=["#E45B35","#E8B44A",JADE],labels={"avg_reliability":"Observed reliability","risk_rate_pct":"Flagged records (%)"})
        fig.update_layout(paper_bgcolor="#FFFCF8",plot_bgcolor="#FFFCF8",font_color=INK)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig=px.bar(score.head(10).sort_values("supplier_health_score"),x="supplier_health_score",y="supplier",orientation="h",title="Supplier health score",color="supplier_health_score",color_continuous_scale=["#E9B1A2",JADE])
        fig.update_layout(paper_bgcolor="#FFFCF8",plot_bgcolor="#FFFCF8",font_color=INK,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    st.dataframe(score,use_container_width=True,hide_index=True)
    st.caption("Health score is an illustrative heuristic based on supplied reliability and observed flags. It is not a certified supplier rating.")

elif page == "Cost Forecasting":
    fc=monthly_forecast(data,6)
    fig=px.line(fc,x="month",y="amount",color="series",markers=True,title="Monthly spend: historical and indicative forecast",color_discrete_map={"Historical":CORAL,"Forecast":JADE})
    fig.update_layout(paper_bgcolor="#FFFCF8",plot_bgcolor="#FFFCF8",font_color=INK,yaxis_title="Spend (₹)",xaxis_title="")
    st.plotly_chart(fig,use_container_width=True)
    future=fc[fc.series=="Forecast"]
    c1,c2=st.columns(2)
    with c1: metric("Next 6-month indicative spend",money(future.amount.sum()),"Trend-blended baseline")
    with c2: metric("Average monthly forecast",money(future.amount.mean() if len(future) else 0),"Planning estimate")
    st.info("Forecast uses a transparent recent-average and trend blend. It is a planning baseline, not a validated time-series model or commitment.")

elif page == "Sourcing Optimizer":
    opt=optimization_candidates(data)
    st.markdown('<div class="note">A decision-support shortlist that balances observed supplier reliability, flagged-record rate and relative unit price. Validate capacity, contract terms, quality and delivery performance before award.</div>',unsafe_allow_html=True)
    st.dataframe(opt[["supplier","spend","transactions","avg_unit_price","supplier_health_score","risk_rate_pct","recommendation_score","recommendation"]],use_container_width=True,hide_index=True)
    top=opt.head(5)
    fig=px.bar(top.sort_values("recommendation_score"),x="recommendation_score",y="supplier",orientation="h",color="recommendation_score",title="Top sourcing candidates",color_continuous_scale=["#F0B5A5",JADE])
    fig.update_layout(paper_bgcolor="#FFFCF8",plot_bgcolor="#FFFCF8",font_color=INK,coloraxis_showscale=False)
    st.plotly_chart(fig,use_container_width=True)
    st.download_button("Export sourcing shortlist",opt.to_csv(index=False).encode(),"procureiq_sourcing_shortlist.csv","text/csv")

else:
    st.markdown('<div class="section"><h3>Dataset health & schema</h3></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: metric("Rows",f"{len(data):,}")
    with c2: metric("Columns",str(len(data.columns)))
    with c3: metric("Missing cells",f"{int(data.isna().sum().sum()):,}")
    st.dataframe(pd.DataFrame({"column":data.columns,"dtype":[str(x) for x in data.dtypes],"missing":[int(data[c].isna().sum()) for c in data.columns]}),use_container_width=True,hide_index=True)
    st.markdown('<div class="section"><h3>Cleaned and enriched records</h3></div>',unsafe_allow_html=True)
    st.dataframe(data,use_container_width=True,hide_index=True)
    st.download_button("Download enriched dataset",data.to_csv(index=False).encode(),"procureiq_enriched_data.csv","text/csv")




st.markdown("""
<style>
.procure-footer {
    margin-top: 55px;
    padding: 55px 20px 25px;
    text-align: center;
    border-top: 1px solid #E4D9D1;
}

.procure-footer .project-title {
    color: #E45B35;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 18px;
}

.procure-footer .developed {
    color: #786B79;
    font-size: 17px;
    margin-bottom: 15px;
}

.procure-footer .developer-name {
    color: #34233D;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 10px;
}

.procure-footer .qualification,
.procure-footer .university {
    color: #786B79;
    font-size: 15px;
    margin-bottom: 7px;
}

.procure-footer .copyright {
    border-top: 1px solid #E4D9D1;
    margin-top: 25px;
    padding-top: 20px;
    color: #786B79;
    font-size: 13px;
}
</style>
<div class="procure-footer">
<div class="project-title">ProcureIQ AI – Enterprise Procurement Intelligence Platform</div>
<div class="developed">Designed & Developed by</div>
<div class="developer-name">Mohamed Riyaz S.</div>
<div class="qualification">Integrated M.Tech CSE | Business Analytics</div>
<div class="university">Vellore Institute of Technology, Chennai</div>
<div class="copyright">© 2026 Mohamed Riyaz S. | All Rights Reserved</div>
</div>
""", unsafe_allow_html=True)
