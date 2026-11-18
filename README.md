# ProcureIQ AI
### Enterprise Procurement Intelligence & Spend Leakage Detection Platform

ProcureIQ AI is an end-to-end Streamlit portfolio application for exploring procurement spend, surfacing invoice and policy exceptions, assessing supplier signals, estimating future expenditure, and producing a sourcing shortlist.

**Designed & developed by Mohamed Riyaz S.**  
Integrated M.Tech Computer Science and Engineering — Business Analytics  
Vellore Institute of Technology, Chennai

## Business problem
Large organizations can lose value through fragmented spend visibility, duplicate invoice references, unusual unit prices, off-policy purchasing, supplier concentration, and weak cost planning. ProcureIQ AI brings these signals into one decision-support workspace.

## Workspaces
1. Executive Command — spend pulse, exposure indicators and priority queue.
2. Spend Intelligence — department/category analysis and supplier concentration.
3. Invoice & Policy Audit — duplicate invoice references, price anomalies and approval exceptions.
4. Supplier Risk — supplier scorecard and reliability-versus-risk view.
5. Cost Forecasting — indicative six-month expenditure baseline.
6. Sourcing Optimizer — transparent supplier shortlist using observed reliability, flags and relative price.
7. Data Studio — schema, data quality and enriched export.

## Quick start
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```
Open the local URL printed by Streamlit.

## Included sample data
`sample_data/procurement_transactions.csv` contains 1,800 synthetic purchase records with seeded examples of repeated invoice IDs, price outliers and off-policy approvals. It is synthetic and must not be represented as real company data.

## Upload your own data
Use the sidebar CSV uploader. Required columns:
- `date`
- `invoice_id`
- `supplier`
- `department`
- `category`
- `quantity`
- `unit_price`
- `amount`
- `approval_status`

Optional fields such as `po_id`, `supplier_country`, and `supplier_reliability` enrich the dashboard. Column names are normalized to lowercase with underscores.

## Methodology and responsible use
- Duplicate invoice flag: repeated `invoice_id` values.
- Price anomaly: robust median absolute deviation score within category.
- Policy exception: approval status contains off-policy / unauthorized / exception.
- Risk score: transparent additive screening heuristic, not a fraud probability.
- Supplier health score: illustrative heuristic from supplied reliability and observed flagged-record rate.
- Forecast: recent-average and trend blend for planning exploration, not a validated forecast.
- Sourcing recommendation: relative score for shortlist exploration, not an automated award decision.

These signals are decision-support aids only. They can produce false positives and false negatives. Always verify against purchase orders, contracts, invoices, delivery/quality records and organizational policy. Do not use the sample data to make real purchasing decisions.

## Suggested production extensions
- PostgreSQL warehouse and role-based access control.
- Three-way matching across PO, goods receipt and invoice.
- Contract price catalogue and supplier quote comparison.
- Delivery lead-time, quality and ESG indicators.
- Model monitoring, threshold calibration and SHAP explanations.
- Approval workflow, audit trail and secure deployment.
- Time-series model validation with rolling backtests.

## Repository structure
```text
ProcureIQ_AI/
├── app.py
├── requirements.txt
├── README.md
├── assets/
│   └── procureiq_logo.svg
├── sample_data/
│   └── procurement_transactions.csv
├── src/
│   └── analytics.py
└── .streamlit/
    └── config.toml
```

## Author
**Mohamed Riyaz S.**  
AI & Machine Learning | Data Science | Business Analytics  
GitHub: https://github.com/Riyaz077  
LinkedIn: https://www.linkedin.com/in/mohamed-riyaz-s07/

---
Portfolio project · Built with Python, Streamlit, Pandas and Plotly.
