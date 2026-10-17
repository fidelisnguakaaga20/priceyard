"""Explicit payment recovery command. No scheduler or API startup integration."""
import argparse
import json


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview recorded payment recovery; --apply verifies existing purchases without charging.")
    parser.add_argument("--apply", action="store_true", help="Explicitly enable provider verification and existing activation rules")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--after-id", type=int, default=0)
    parser.add_argument("--ceiling-id", type=int)
    parser.add_argument("--time-budget-seconds", type=float, default=45)
    options = parser.parse_args(argv)
    # Settings/engine are loaded only on explicit invocation, never app import.
    from app.database import get_engine
    from app.services.payment_reconciliation_service import reconcile_payments
    try:
        report = reconcile_payments(get_engine(), apply=options.apply, limit=options.limit,
                                    after_id=options.after_id, ceiling_id=options.ceiling_id,
                                    time_budget_seconds=options.time_budget_seconds)
    except Exception:
        # Connection/configuration errors can contain sensitive connection context.
        print(json.dumps({"error": "Payment reconciliation could not complete"}))
        return 2
    print(json.dumps(report))  # IDs/outcomes only; no provider bodies or credentials.
    return 0 if not report["busy"] and not any(row["outcome"] in {"error", "missing_record"} for row in report["outcomes"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
