import csv
import tempfile
import unittest
from pathlib import Path
from cloudcost.engine import analyze, load_records
from cloudcost.report import render_html


class EngineTests(unittest.TestCase):
    def example(self):
        return [{"date": f"2026-11-{d:02d}", "service": "EC2", "cost_usd": cost}
                for d, cost in [(1, 10), (2, 11), (3, 9), (4, 90)]]

    def test_spike_detected(self):
        self.assertEqual(len(analyze(self.example())["anomalies"]), 1)

    def test_spike_baseline(self):
        self.assertEqual(analyze(self.example())["anomalies"][0]["baseline_usd"], 10)

    def test_no_anomaly_before_three_days(self):
        self.assertFalse(analyze(self.example()[:3])["anomalies"])

    def test_overspend(self):
        self.assertEqual(analyze(self.example(), budget=100)["budget_status"], "OVER")

    def test_near_budget(self):
        self.assertEqual(analyze(self.example()[:3], budget=35)["budget_status"], "NEAR")

    def test_total(self):
        self.assertEqual(analyze(self.example())["total_usd"], 120)

    def test_empty(self):
        self.assertEqual(analyze([])["total_usd"], 0)

    def test_negative_budget(self):
        with self.assertRaises(ValueError):
            analyze([], budget=0)

    def test_html_escape(self):
        result = analyze([{"date": "2026-11-01", "service": "<script>", "cost_usd": 1}])
        self.assertIn("&lt;script&gt;", render_html(result))

    def test_load_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            path.write_text("date,service,cost_usd\n2026-11-01,EC2,3.50\n", encoding="utf-8")
            self.assertEqual(load_records(path)[0]["cost_usd"], 3.5)

    def test_bad_date(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            path.write_text("date,service,cost_usd\nbad,EC2,3\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(path)

    def test_bad_cost(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            path.write_text("date,service,cost_usd\n2026-11-01,EC2,-1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(path)

    def test_missing_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            path.write_text("date,cost_usd\n2026-11-01,3\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(path)


if __name__ == "__main__":
    unittest.main()
