"""Optional Streamlit interface. CLI works without third-party dependencies."""
import json
from pathlib import Path
import streamlit as st
from cloudcost.engine import analyze, load_records
from cloudcost.report import render_html

st.set_page_config(page_title="CloudCost Guard", page_icon="☁️", layout="wide")
st.title("☁️ CloudCost Guard")
st.caption("Offline cloud billing explorer. Upload a CSV with date, service, cost_usd.")
upload = st.file_uploader("Upload daily cloud billing CSV", type="csv")
budget = st.number_input("Budget for the uploaded period (USD)", min_value=1.0, value=500.0, step=50.0)
if upload:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        temp.write(upload.getvalue())
        filename = temp.name
    try:
        records = load_records(filename)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    finally:
        Path(filename).unlink(missing_ok=True)
else:
    records = load_records(Path(__file__).parent / "samples" / "daily_billing.csv")
result = analyze(records, budget=budget)
a, b, c, d = st.columns(4)
a.metric("Total spend", f"${result['total_usd']:,.2f}")
b.metric("Budget usage", f"{result['budget_used_pct']}%")
c.metric("Budget status", result["budget_status"])
d.metric("Unusual service-days", len(result["anomalies"]))
st.subheader("Daily spend")
st.line_chart({r['date']: r['cost_usd'] for r in result['by_day']})
st.subheader("Spend by service")
st.bar_chart({r['service']: r['cost_usd'] for r in result['by_service']})
st.subheader("Flagged anomalies")
st.dataframe(result['anomalies'], use_container_width=True)
st.download_button("Download JSON", json.dumps(result, indent=2), file_name="cloudcost_report.json", mime="application/json")
st.download_button("Download HTML report", render_html(result), file_name="cloudcost_report.html", mime="text/html")
st.info("These are offline heuristics on supplied records, not live AWS billing data or an AWS Cost Explorer integration.")
