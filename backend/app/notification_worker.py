"""Explicit worker command; importing this module never sends notifications."""
import argparse

from app.database import get_session_factory
from app.services.notification_service import process_notifications


def main() -> int:
    parser = argparse.ArgumentParser(description="Process a bounded PriceYard notification batch")
    parser.add_argument("--limit", type=int, default=50, choices=range(1, 101), metavar="1..100")
    options = parser.parse_args()
    with get_session_factory()() as db:
        counts = process_notifications(db, limit=options.limit)
    print(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
