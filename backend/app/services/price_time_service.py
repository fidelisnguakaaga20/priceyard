"""Owner-approved Nigerian price days; billing continues using its UTC rules."""
from datetime import date, datetime, time, timedelta, timezone


NIGERIA_TIME = timezone(timedelta(hours=1), name="WAT")


def price_day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=NIGERIA_TIME)
    return start.astimezone(timezone.utc), (start + timedelta(days=1)).astimezone(timezone.utc)
