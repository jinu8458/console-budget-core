from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from budget_app.errors import AppError, NotFoundError, ValidationError
from budget_app.services import LedgerService, SearchFilter
from budget_app.storage import read_jsonl, rewrite_jsonl


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = LedgerService(self.root)
        self.ledger.initialize()

    def test_edits_and_category_migration_survive_reopening(self):
        tx = self.ledger.add_transaction("2026-11-01", "expense", "food", 5000, "점심")
        self.ledger.update_transaction(tx.id, amount="6500", tags="lunch, work")
        self.ledger.add_category("meal")
        self.assertEqual(self.ledger.remove_category("food", replace_with="meal"), 1)
        reopened = LedgerService(self.root)
        saved = reopened.get_transaction(tx.id)
        self.assertEqual((saved.amount, saved.category, saved.tags), (6500, "meal", ["lunch", "work"]))
        self.assertNotIn("food", reopened.categories.names())
        reopened.delete_transaction(tx.id)
        with self.assertRaises(NotFoundError):
            LedgerService(self.root).get_transaction(tx.id)

    def test_month_filter_summary_and_budget_boundary(self):
        self.ledger.set_budget("2026-11", 10_000)
        self.ledger.add_transaction("2026-10-31", "expense", "food", 99_000)
        self.ledger.add_transaction("2026-11-01", "income", "salary", 100_000)
        first = self.ledger.add_transaction("2026-11-02", "expense", "food", 10_000, "Lunch", ["work"])
        summary = self.ledger.monthly_summary("2026-11")
        self.assertEqual((summary.income, summary.expense, summary.balance, summary.count), (100_000, 10_000, 90_000, 2))
        self.assertEqual(summary.usage_rate, 100.0)
        self.assertFalse(summary.over_budget)
        second = self.ledger.add_transaction("2026-11-02", "expense", "transport", 1)
        self.assertTrue(self.ledger.monthly_summary("2026-11").over_budget)
        self.assertEqual(self.ledger.latest(limit=1)[0].id, second.id)
        found = self.ledger.latest(SearchFilter(month="2026-11", q="lunch", tag="work"))
        self.assertEqual([tx.id for tx in found], [first.id])

    def test_failed_rewrite_preserves_original_file(self):
        self.ledger.add_transaction("2026-11-01", "expense", "food", 5000)
        path = self.ledger.transactions.path
        original = path.read_bytes()

        def broken_records():
            yield {"temporary": True}
            raise RuntimeError("Interrupted write")

        with self.assertRaises(RuntimeError):
            rewrite_jsonl(path, broken_records())
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(self.root.glob(".*.tmp")), [])

    def test_invalid_input_and_corrupt_json_are_reported(self):
        for date, amount in [("2026-02-30", 1000), ("2026-11-01", 0)]:
            with self.subTest(date=date, amount=amount), self.assertRaises(ValidationError):
                self.ledger.add_transaction(date, "expense", "food", amount)
        self.assertEqual(list(self.ledger.stream()), [])
        path = self.root / "damaged.jsonl"
        path.write_text('{"ok": true}\nnot json\n', encoding="utf-8")
        rows = read_jsonl(path)
        self.assertEqual(next(rows), {"ok": True})
        with self.assertRaisesRegex(AppError, "2"):
            next(rows)


if __name__ == "__main__":
    unittest.main()
