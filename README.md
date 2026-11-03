# CloudCost Guard ☁️

Offline cloud billing analyzer and spend anomaly explorer built with Python. Includes a Streamlit dashboard, CLI, explainable spending spike detection, budget flags, JSON/HTML exports, and GitHub Actions tests.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Load daily cloud spending records from CSV (`date,service,cost_usd`)
- Sum spending per service and day
- Detect daily service spending spikes compared with up to seven preceding **recorded** days of that service (minimum three)
- Track spending against a configurable budget for the **uploaded period**
- Download JSON and HTML reports
- Unit-tested core with no third-party dependencies
- Optional Streamlit dashboard; no cloud account or API key required

> Educational offline cost monitoring example. It **does not** access AWS Cost Explorer or send live alerts. It is not a billing forecast. The example CSV is simulated.

## Run (Windows PowerShell / CMD)

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run dashboard.py
```

Open http://localhost:8501. The sample CSV loads by default; upload your own data to explore another period.

## Command line mode (no dependencies to install)

```bash
python -m cloudcost.cli samples/daily_billing.csv --budget 900 --json report.json --html report.html
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Input schema

| Column | Example | Notes |
|---|---|---|
| `date` | `2026-10-10` | ISO 8601 day |
| `service` | `EC2` | Free text |
| `cost_usd` | `27.40` | Non-negative number |

Multiple rows with the same date/service are added together. Treat the CSV as a single budget period. Budget thresholds: OK <80%, NEAR 80-100%, OVER >100%.

## Detection method

For each service and date, compare that day's spend to **up to seven prior recorded daily totals** (not calendar-day filling). Minimum three prior days. Flag when:

1. current spend >= average + 2.5 × max(population standard deviation, $2), and
2. current spend >= 1.5 × prior average, and
3. current > prior average.

These are heuristic flags for investigation, not guarantees of unexpected cost or statistically calibrated confidence.

## Project structure

```text
cloudcost-guard/
├── cloudcost/
│   ├── __init__.py
│   ├── engine.py
│   ├── report.py
│   └── cli.py
├── dashboard.py
├── samples/daily_billing.csv
├── tests/test_engine.py
├── .github/workflows/tests.yml
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Possible enhancements

- AWS Cost Explorer `GetCostAndUsage` ingestion with IAM least privilege
- Budget schedules and email alerts
- Day-of-week seasonality and statistical time-series forecasting
- Per-account or per-tag breakdown and currency support

## Privacy and security

All processing is local. Use only files you are authorized to analyze. HTML report content is escaped to prevent stored script markup in service labels.

## License

MIT.
