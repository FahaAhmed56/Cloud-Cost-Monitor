"""Cloud spend analysis based on daily service cost records."""
from __future__ import annotations
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, pstdev

REQUIRED = {"date", "service", "cost_usd"}


def load_records(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("CSV needs date, service, cost_usd columns")
        records = []
        for line_no, row in enumerate(reader, start=2):
            try:
                day = date.fromisoformat((row["date"] or "").strip())
                service = (row["service"] or "").strip()
                cost = float(row["cost_usd"])
                if not service or not 0 <= cost < 1e12 or cost != cost:
                    raise ValueError()
            except (ValueError, TypeError, OverflowError):
                raise ValueError(f"Invalid record on CSV line {line_no}") from None
            records.append({"date": day.isoformat(), "service": service, "cost_usd": round(cost, 2)})
        return records


def analyze(records: list[dict], budget: float = 500.0, threshold: float = 2.5) -> dict:
    """Compare daily totals with baseline, flag large positive deviations.

    Rule: at least 3 previous recorded days for the same service, then
    current >= baseline mean + threshold * max(population std, $2), and
    current >= 1.5 * mean. This is a heuristic, not forecasting.
    """
    if budget <= 0 or threshold <= 0:
        raise ValueError("Budget and threshold must be positive")
    grouped = defaultdict(float)
    for record in records:
        grouped[(record["date"], record["service"])] += record["cost_usd"]
    days = defaultdict(list)
    service_costs = defaultdict(float)
    for (day, service), amount in sorted(grouped.items()):
        days[service].append((day, round(amount, 2)))
        service_costs[service] += amount
    anomalies = []
    for service, observations in sorted(days.items()):
        for index, (day, amount) in enumerate(observations):
            historical = [cost for _, cost in observations[max(0, index - 7):index]]
            if len(historical) < 3:
                continue
            baseline = mean(historical)
            deviation = pstdev(historical)
            cutoff = baseline + threshold * max(deviation, 2.0)
            if amount >= cutoff and amount >= baseline * 1.5 and amount > baseline:
                anomalies.append({"date": day, "service": service, "cost_usd": amount,
                                  "baseline_usd": round(baseline, 2),
                                  "increase_pct": round((amount / baseline - 1) * 100, 1) if baseline else None})
    total = round(sum(service_costs.values()), 2)
    by_day = defaultdict(float)
    for (day, _service), amount in grouped.items():
        by_day[day] += amount
    return {
        "total_usd": total,
        "budget_usd": round(budget, 2),
        "remaining_usd": round(budget - total, 2),
        "budget_used_pct": round(total / budget * 100, 1),
        "budget_status": "OVER" if total > budget else "NEAR" if total >= budget * 0.8 else "OK",
        "by_service": [{"service": k, "cost_usd": round(v, 2)} for k, v in sorted(service_costs.items(), key=lambda x: -x[1])],
        "by_day": [{"date": k, "cost_usd": round(v, 2)} for k, v in sorted(by_day.items())],
        "anomalies": sorted(anomalies, key=lambda row: (row["date"], row["service"])),
        "records": len(records),
    }
