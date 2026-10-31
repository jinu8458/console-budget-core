"""임시 폴더에서 거래 저장과 월별 집계를 실행한다."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from budget_app.services import LedgerService, SearchFilter


def main() -> None:
    with TemporaryDirectory() as folder:
        ledger = LedgerService(Path(folder))
        ledger.initialize()
        ledger.set_budget("2026-11", 300_000)
        ledger.add_transaction("2026-11-01", "income", "salary", 1_000_000, "예시 수입")
        ledger.add_transaction("2026-11-01", "expense", "food", 12_000, "예시 점심", ["lunch"])
        ledger.add_transaction("2026-11-02", "expense", "transport", 3_000, "예시 교통비")

        reopened = LedgerService(Path(folder))
        summary = reopened.monthly_summary("2026-11")
        print(f"수입: {summary.income:,}원")
        print(f"지출: {summary.expense:,}원")
        print(f"잔액: {summary.balance:,}원")
        print(f"예산 사용률: {summary.usage_rate:.1f}%")
        print("식비:", [(tx.date, tx.amount) for tx in reopened.latest(SearchFilter(category="food"))])


if __name__ == "__main__":
    main()
