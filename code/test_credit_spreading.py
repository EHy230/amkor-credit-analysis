"""Offline engineering tests, not a live Claude accuracy evaluation."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import credit_spreading as c


class PipelineTests(unittest.TestCase):
    def record(self, field="revenue", raw=6707981, year=2025):
        return {"field_id": field, "fiscal_year": year, "raw_value": raw,
                "reported_unit": "USD thousands", "source_id": "AMKR_2025_10K",
                "pdf_page_1_based": 54, "printed_page": "53", "source_label": "Net sales",
                "source_quote": "Net sales $ 6,707,981 $ 6,317,692 $ 6,503,065",
                "status": "found", "note": "", "job_id": "income"}

    def page(self):
        return {("AMKR_2025_10K", 54): "AMKOR\n2025 2024 2023\n(In thousands)\nNet sales $ 6,707,981 $ 6,317,692 $ 6,503,065\n53"}

    def test_unit_conversion_and_signed_flows(self):
        self.assertAlmostEqual(c.normalize_value(6707981, "USD thousands", "revenue"), 6707.981)
        self.assertAlmostEqual(c.normalize_value(-904614, "USD thousands", "cash_capex"), 904.614)
        self.assertAlmostEqual(c.normalize_value(-885044, "USD thousands", "investing_cash_flow"), -885.044)
        self.assertAlmostEqual(c.normalize_value(-2221, "USD thousands", "nci_net_income"), 2.221)
        self.assertIsNone(c.normalize_value(None, "unknown", "revenue"))
        for raw in [True, float("nan"), float("inf"), "123"]:
            with self.assertRaises(ValueError):
                c.normalize_value(raw, "USD thousands", "revenue")

    def test_explicit_dash_zero(self):
        self.assertEqual(c.money_tokens("Payments — (9,731) (19,448)"), [0, -9731, -19448])
        self.assertEqual(c.money_tokens("FX effect on cash2,549 (14,417) (10,692)"), [2549, -14417, -10692])
        self.assertEqual(c.normalize_value(0, "USD thousands", "short_term_debt_repaid"), 0)

    def test_evidence_good(self):
        self.assertEqual(c.validate_evidence(self.record(), self.page()), [])

    def test_wrong_year_column(self):
        self.assertIn("amount_not_in_requested_year_column", c.validate_evidence(self.record(year=2024), self.page()))

    def test_wrong_page_unit_fabricated_quote(self):
        record = self.record()
        record["pdf_page_1_based"] = 53
        self.assertEqual(c.validate_evidence(record, self.page()), ["wrong_source_or_page"])
        record = self.record()
        record["reported_unit"] = "USD millions"
        record["printed_page"] = "54"
        record["source_quote"] = "Net sales 1 2 3"
        problems = c.validate_evidence(record, self.page())
        self.assertIn("wrong_or_missing_unit", problems)
        self.assertIn("printed_page_mismatch", problems)
        self.assertIn("quote_not_found_on_page", problems)

    def benchmark(self):
        return [{"field_id": f, "fiscal_year": y, "statement": s, "normalized_usd_millions": 1.0}
                for f, _, s, _ in c.SPECS for y in (2023, 2024, 2025)]

    def test_missing_is_not_zero_or_pass(self):
        evaluated, summary = c.evaluate([], self.benchmark(), {})
        self.assertEqual(summary["numeric_accuracy_all_planned"], 0)
        self.assertEqual(summary["numeric_coverage"], 0)
        self.assertTrue(all(r["normalized_usd_millions"] is None for r in evaluated))
        self.assertTrue(all(r["status"] == "UNAVAILABLE" for r in c.reconciliations(evaluated)))

    def test_duplicate_and_unexpected_key(self):
        record = self.record()
        evaluated, _ = c.evaluate([record, copy.deepcopy(record)], self.benchmark(), self.page())
        flagged = next(r for r in evaluated if r["field_id"] == "revenue" and r["fiscal_year"] == 2025)
        self.assertIn("duplicate_record", flagged["issues"])
        with self.assertRaises(ValueError):
            c.evaluate([dict(record, field_id="unknown")], self.benchmark(), self.page())

    def test_no_benchmark_in_request(self):
        payload = json.loads(c.request_payload(c.jobs()[0], self.page()))
        self.assertNotIn("benchmark", payload)
        self.assertNotIn("normalized_usd_millions", payload)
        self.assertNotIn("benchmark", c.output_schema()["properties"])

    def test_paid_opt_in_precedes_import_or_network(self):
        with self.assertRaises(ValueError):
            c.extract_live({}, "fake-key", "not_created")

    def test_csv_injection_and_review_gate(self):
        self.assertEqual(c.safe_csv_value("=HYPERLINK(\"x\")"), "'=HYPERLINK(\"x\")")
        self.assertEqual(c.safe_csv_value(-5), -5)
        with tempfile.TemporaryDirectory() as folder:
            staged = [{"field_id": "revenue", "fiscal_year": 2025, "normalized_usd_millions": 1,
                       "evidence_checks_pass": True}]
            rows = [dict(staged[0], reviewer_decision="Pending", reviewer_name="", review_note="")]
            path, output = Path(folder) / "review.csv", Path(folder) / "approved.csv"
            c.write_csv(path, rows)
            with self.assertRaises(ValueError):
                c.approve_reviewed(path, staged, output)
            self.assertFalse(output.exists())
            rows[0].update(reviewer_decision="Approve", reviewer_name="Analyst", review_note="Checked source row/year/unit")
            c.write_csv(path, rows)
            self.assertEqual(len(c.approve_reviewed(path, staged, output)), 1)
            rows[0]["normalized_usd_millions"] = 1000
            c.write_csv(path, rows)
            with self.assertRaises(ValueError):
                c.approve_reviewed(path, staged, output)

    def test_timing_unmeasured_and_fair_comparison(self):
        self.assertEqual(c.timing_comparison(None, None, None, False)["status"], "NOT_MEASURED")
        self.assertEqual(c.timing_comparison(100, 20, 30, False)["status"], "NOT_COMPARABLE_UNTIL_REVIEW_COMPLETE")
        self.assertEqual(c.timing_comparison(100, 20, 30, True)["fraction_time_saved"], .5)
        with self.assertRaises(ValueError):
            c.timing_comparison(0, 20, 30, True)

    def test_job_partition_is_complete(self):
        keys = [(field, year) for job in c.jobs() for field in job['fields'] for year in job['years']]
        self.assertEqual(len(keys), 174)
        self.assertEqual(len(set(keys)), 174)
        self.assertEqual(set(keys), c.expected_keys())


if __name__ == "__main__":
    unittest.main(verbosity=2)
