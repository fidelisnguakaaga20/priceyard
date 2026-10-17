import csv
from datetime import date, datetime, timedelta, timezone
from io import StringIO
import unittest
from unittest.mock import patch

import anyio
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.routes.report_export_routes import _PriceReportResponse
from app.security import create_access_token
from app.services.report_export_service import CSV_HEADERS, stream_price_report_csv


def seed_export(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic export owner", email="export-stream@example.com",
                     password_hash="unused", role="admin", referral_code="STREAMCSV")
        # Original Admin exports include approved history from inactive catalogs.
        commodity = Commodity(name="Egusi", is_active=False)
        market = Market(name="Kwali Market")
        db.add_all([owner, commodity, market])
        db.flush()
        start = datetime(2026, 10, 1, tzinfo=timezone.utc)
        for index in range(253):
            row = PriceUpdate(commodity_id=commodity.id, market_id=market.id,
                price_low=210000 + index, price_high=220000 + index, unit="1 bag",
                movement="unknown", confidence_level="Low confidence",
                update_date_time=start + timedelta(days=index // 100),
                status="approved" if index < 251 else "pending", created_by=owner.id,
                source_1="PRIVATE-EXPORT-SOURCE", is_outdated=index == 0)
            db.add(row)
            if index == 0:
                db.flush()
                db.add(MarketSignal(commodity_id=commodity.id, market_id=market.id,
                    price_update_id=row.id, signal_type="=unsafe", signal_description="Synthetic",
                    created_by=owner.id))
        db.commit()
        return owner.id


def check_streaming_export(check, engine):
    seed_export(engine)
    with Session(engine) as db:
        before = db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all()
    loaded = []
    live_counts = []

    def observe(db, instance):
        if isinstance(instance, PriceUpdate):
            loaded.append(instance.id)
            live_counts.append(sum(isinstance(value, PriceUpdate) for value in db.identity_map.values()))

    event.listen(Session, "loaded_as_persistent", observe)
    try:
        stream = stream_price_report_csv(engine)
        check.assertEqual(next(stream), ",".join(CSV_HEADERS) + "\r\n")
        check.assertEqual(loaded, [])
        first = next(stream)
        check.assertLessEqual(len(loaded), 100)
        content = first + "".join(stream)
    finally:
        event.remove(Session, "loaded_as_persistent", observe)
    rows = list(csv.reader(StringIO(content)))
    check.assertEqual(len(rows), 251)
    check.assertEqual([row[2] for row in rows], [f"{210000+i}.00" for i in range(251)])
    check.assertEqual(len(loaded), 251)
    # SQLAlchemy can build the next batch before releasing the previous one.
    check.assertLessEqual(max(live_counts), 200)
    check.assertEqual(rows[0][11], "'=unsafe: Synthetic")
    check.assertNotIn("PRIVATE-EXPORT-SOURCE", content)
    check.assertEqual(len(rows[-1]), len(CSV_HEADERS))
    with Session(engine) as db:
        check.assertEqual(db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all(), before)
    # A partially consumed download must also return its cursor/connection.
    stream = stream_price_report_csv(engine)
    next(stream)
    next(stream)
    stream.close()
    if hasattr(engine.pool, "checkedout"):
        check.assertEqual(engine.pool.checkedout(), 0)


class ReportExportStreamingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_complete_ordered_export_uses_bounded_entity_batches_and_preserves_history(self):
        check_streaming_export(self, self.engine)

    def test_filters_empty_export_and_invalid_dates(self):
        seed_export(self.engine)
        rows = list(csv.reader(StringIO("".join(stream_price_report_csv(self.engine,
            commodity_search="gusi", market_search="wali", date_from=date(2026, 10, 2), date_to=date(2026, 10, 2))))))
        self.assertEqual(len(rows), 101)
        self.assertEqual(rows[1][2], "210100.00")
        self.assertEqual(rows[-1][2], "210199.00")
        self.assertEqual("".join(stream_price_report_csv(self.engine, commodity_search="No match")),
                         ",".join(CSV_HEADERS) + "\r\n")
        with self.assertRaises(HTTPException) as error:
            stream_price_report_csv(self.engine, date_from=date(2026, 10, 3), date_to=date(2026, 10, 1))
        self.assertEqual(error.exception.status_code, 422)

    def test_original_route_access_download_and_validation(self):
        admin_id = seed_export(self.engine)
        def sessions():
            with Session(self.engine) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        with TestClient(app) as client:
            self.assertEqual(client.get("/reports/prices.csv").status_code, 401)
            headers = {"Authorization": "Bearer " + create_access_token(user_id=admin_id)}
            response = client.get("/reports/prices.csv", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(list(csv.reader(StringIO(response.text)))), 252)
            self.assertIn('filename="priceyard-price-report.csv"', response.headers["content-disposition"])
            self.assertNotIn("content-length", response.headers)
            self.assertEqual(client.get("/reports/prices.csv?date_from=2026-10-03&date_to=2026-10-01", headers=headers).status_code, 422)
            with Session(self.engine) as db:
                db.get(User, admin_id).role = "reporter"
                db.commit()
            self.assertEqual(client.get("/reports/prices.csv", headers=headers).status_code, 403)

    def test_failed_download_closes_stream(self):
        closed = []
        def chunks():
            try:
                yield "header\r\n"
                yield "record\r\n"
            finally:
                closed.append(True)
        async def send(message):
            if message["type"] == "http.response.body":
                raise OSError("Synthetic disconnected client")
        async def receive():
            return {"type": "http.disconnect"}
        async def run():
            response = _PriceReportResponse(chunks(), media_type="text/csv")
            with self.assertRaises(Exception):
                await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
        anyio.run(run)
        self.assertEqual(closed, [True])

    def test_database_error_closes_export_session(self):
        seed_export(self.engine)
        with patch("app.services.report_export_service.Session") as sessions:
            sessions.return_value.__enter__.return_value.scalars.side_effect = RuntimeError("Synthetic failure")
            with self.assertRaises(RuntimeError):
                next(stream_price_report_csv(self.engine))
            sessions.return_value.__exit__.assert_called_once()
