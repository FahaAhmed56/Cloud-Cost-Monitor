"""Command line runner: python -m cloudcost.cli."""
import argparse
import json
from pathlib import Path
from .engine import load_records, analyze
from .report import render_html


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline cloud cost insights from CSV")
    parser.add_argument("csv", help="CSV with date,service,cost_usd")
    parser.add_argument("--budget", type=float, default=500)
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--html", dest="html_path")
    args = parser.parse_args(argv)
    result = analyze(load_records(args.csv), budget=args.budget)
    print(json.dumps(result, indent=2))
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.html_path:
        Path(args.html_path).write_text(render_html(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
