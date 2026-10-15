"""Recorded measurement labels, never inferred physical conversions."""

from datetime import date, datetime, time, timedelta, timezone
import json


LAGOS_TIMEZONE = timezone(timedelta(hours=1), name="Africa/Lagos")
FUTURE_OBSERVATION_TOLERANCE = timedelta(minutes=5)


def normalize_label(value: str | None) -> str:
    # Match the database lower(trim(label)) expression. Do not infer a bag
    # weight, grade, commodity variant, or equivalence between different units.
    return value.strip().lower() if value else ""


def series_key(item) -> str:
    labels = (item.unit, item.bag_size, item.commodity_type, item.grade)
    components = [item.commodity_id, item.market_id, *(normalize_label(value) for value in labels)]
    if not normalize_label(item.bag_size):
        components.append(f"unspecified:{item.id}")
    return json.dumps(components, ensure_ascii=True, separators=(",", ":"))


def lagos_day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=LAGOS_TIMEZONE)
    return start.astimezone(timezone.utc), (start + timedelta(days=1)).astimezone(timezone.utc)


def validate_observation_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Observation time must include a timezone offset")
    normalized = value.astimezone(timezone.utc)
    if normalized > datetime.now(timezone.utc) + FUTURE_OBSERVATION_TOLERANCE:
        raise ValueError("Observation time cannot be more than five minutes in the future")
    return normalized
