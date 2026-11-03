"""Safe offline HTML report rendering."""
import html


def render_html(result: dict) -> str:
    service_rows = "".join(
        f"<tr><td>{html.escape(row['service'])}</td><td>${row['cost_usd']:.2f}</td></tr>"
        for row in result["by_service"]
    )
    anomaly_rows = "".join(
        f"<tr><td>{html.escape(row['date'])}</td><td>{html.escape(row['service'])}</td>"
        f"<td>${row['cost_usd']:.2f}</td><td>${row['baseline_usd']:.2f}</td></tr>"
        for row in result["anomalies"]
    ) or "<tr><td colspan='4'>No anomalies flagged</td></tr>"
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>CloudCost Guard Report</title><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;padding:0 16px;color:#172238}}
h1{{color:#1d4ed8}}.kpis{{display:flex;gap:12px;flex-wrap:wrap}}.kpis div{{background:#edf2ff;padding:18px;border-radius:12px;min-width:160px}}
table{{border-collapse:collapse;width:100%;margin:12px 0 30px}}th,td{{border-bottom:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#f4f6fa}}small{{color:#64748b}}</style></head><body><h1>CloudCost Guard</h1>
<p>Offline cloud billing analysis (input period, not necessarily monthly).</p>
<div class='kpis'><div>Total<br><strong>${result['total_usd']:.2f}</strong></div>
<div>Budget<br><strong>${result['budget_usd']:.2f}</strong></div>
<div>Budget status<br><strong>{result['budget_status']}</strong></div>
<div>Anomalies<br><strong>{len(result['anomalies'])}</strong></div></div>
<h2>Spend by service</h2><table><tr><th>Service</th><th>Cost</th></tr>{service_rows}</table>
<h2>Unusual daily costs</h2><table><tr><th>Date</th><th>Service</th><th>Cost</th><th>Prior average</th></tr>{anomaly_rows}</table>
<small>Heuristic findings on imported data. Verify against your cloud provider before taking action.</small></body></html>"""
