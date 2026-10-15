"""Synthetic price regression tests; execute only with the isolated P00 runner."""

import csv
import unittest
from unittest.mock import patch
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from io import StringIO

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.models.buying_zone import BuyingZone
from app.models.commodity import Commodity
from app.models.cost_breakdown import CostBreakdown
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_revision import PriceRevision
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.routes import market_signal_routes, price_update_routes, quality_signal_routes
from app.schemas.cost_breakdown_schema import CostBreakdownCreate, CostBreakdownUpdate
from app.schemas.price_update_schema import PriceUpdateCreate, PriceUpdateUpdate
from app.services.cost_breakdown_service import create_cost_breakdown, delete_cost_breakdown, update_cost_breakdown
from app.services.intelligence_query_service import list_intelligence
from app.services.market_signal_service import delete_market_signal
from app.services.price_update_service import (
    approve_price_update, count_latest_approved_price_updates, create_price_update, delete_price_update, get_approved_price_update,
    list_latest_approved_price_updates, list_price_history, mark_price_update_outdated, update_price_update,
)
from app.services.report_export_service import build_price_report_csv, spreadsheet_safe_text, list_exportable_price_updates
from app.services.subscription_service import build_trial_subscription
from app.utils.permissions import get_current_user, optional_current_user
from app.utils.price_measurement import lagos_day_bounds


class PriceIntegrityTests(unittest.TestCase):
    def test_large_csv_export_is_explicitly_rejected_and_can_be_filtered_without_losing_rows(self):
        for offset in range(3):
            self.approved(update_date_time=self.when + timedelta(days=offset))
        with patch("app.services.report_export_service.MAX_EXPORT_ROWS", 2):
            with self.assertRaises(HTTPException) as caught:
                list_exportable_price_updates(self.db)
            self.assertEqual(caught.exception.status_code, 422)
            self.assertEqual(len(list_exportable_price_updates(self.db, date_to=self.when.date())), 1)
        self.assertEqual(len(list_exportable_price_updates(self.db)), 3)

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool,
                                    connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, autoflush=False)
        self.admin = User(full_name="Synthetic Administrator", email="admin@price-tests.test",
                          password_hash="unused-test-hash", role="admin", is_active=True, referral_code="PRICEADMIN")
        self.trial = User(full_name="Synthetic Subscriber", email="trial@price-tests.test",
                          password_hash="unused-test-hash", role="free_user", is_active=True, referral_code="PRICETRIAL")
        self.trial.subscription = build_trial_subscription(user=self.trial)
        self.free = User(full_name="Synthetic Free", email="free@price-tests.test",
                         password_hash="unused-test-hash", role="free_user", is_active=True, referral_code="PRICEFREE")
        self.commodity = Commodity(name="Synthetic Egusi", is_active=True)
        self.market = Market(name="Synthetic Market", state="Synthetic State", is_active=True)
        self.db.add_all([self.admin, self.trial, self.free, self.commodity, self.market])
        self.db.commit()
        self.when = datetime(2026, 1, 10, 12, tzinfo=timezone.utc)
        self.reader = None
        application = FastAPI()
        for router in (price_update_routes.router, market_signal_routes.router, quality_signal_routes.router):
            application.include_router(router)

        def database_override():
            yield self.db

        def authenticated_override():
            if self.reader is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            return self.reader

        application.dependency_overrides[get_db] = database_override
        application.dependency_overrides[optional_current_user] = lambda: self.reader
        application.dependency_overrides[get_current_user] = authenticated_override
        self.client = TestClient(application)

    def tearDown(self):
        self.client.close()
        self.db.close()
        self.engine.dispose()

    def make_price(self, **changes):
        values = dict(commodity_id=self.commodity.id, market_id=self.market.id,
                      price_low=Decimal("90.00"), price_high=Decimal("110.00"), average_price=Decimal("100.00"),
                      unit="bag", bag_size="50 kg", commodity_type="shelled", grade="A",
                      confidence_level="Admin confirmed", suggested_action="Watch", possible_meaning="Synthetic premium meaning",
                      notes="Synthetic premium note", source_1="Synthetic source one", source_2="Synthetic source two",
                      update_date_time=self.when)
        values.update(changes)
        return create_price_update(self.db, PriceUpdateCreate(**values), self.admin)

    def approved(self, **changes):
        return approve_price_update(self.db, self.make_price(**changes), self.admin)

    def test_current_and_history_preserve_measurement_series(self):
        old = self.approved()
        latest = self.approved(update_date_time=self.when + timedelta(hours=1), unit=" BAG ", bag_size=" 50 KG ")
        different_bag = self.approved(bag_size="100 kg")
        different_grade = self.approved(grade="B")
        current = list_latest_approved_price_updates(self.db)
        self.assertEqual({item.id for item in current}, {latest.id, different_bag.id, different_grade.id})
        self.assertEqual(len(list_price_history(self.db)), 4)
        self.assertNotIn(old.id, {item.id for item in current})

    def test_outdated_latest_does_not_resurface_older_observation(self):
        old = self.approved()
        latest = self.approved(update_date_time=self.when + timedelta(hours=1))
        mark_price_update_outdated(self.db, latest, actor=self.admin)
        self.assertEqual(list_latest_approved_price_updates(self.db), [])
        self.assertEqual({item.id for item in list_price_history(self.db)}, {old.id, latest.id})
        self.assertEqual(self.client.get(f"/price-updates/{old.id}").status_code, 404)
        self.assertEqual(self.client.get(f"/price-updates/{latest.id}").status_code, 404)

    def test_movement_filter_applies_after_latest_selection(self):
        self.approved()
        self.approved(price_low=100, price_high=120, average_price=110, update_date_time=self.when + timedelta(hours=1))
        latest = self.approved(price_low=80, price_high=100, average_price=90, update_date_time=self.when + timedelta(hours=2))
        self.assertEqual(list_latest_approved_price_updates(self.db, movement="up"), [])
        self.assertEqual([item.id for item in list_latest_approved_price_updates(self.db, movement="down")], [latest.id])

    def test_comparison_uses_recorded_average_and_identified_predecessor(self):
        previous = self.approved(average_price=95)
        current = self.approved(average_price=100, update_date_time=self.when + timedelta(hours=1))
        self.assertEqual(current.previous_price_update_id, previous.id)
        self.assertEqual(current.previous_price_low, Decimal("90.00"))
        self.assertEqual(current.movement, "up")
        self.assertEqual(previous.average_price, Decimal("95.00"))

    def test_missing_recorded_average_remains_null_and_movement_unknown(self):
        self.approved()
        current = self.approved(average_price=None, update_date_time=self.when + timedelta(hours=1))
        self.assertIsNone(current.average_price)
        self.assertEqual(current.movement, "unknown")
        payload = PriceUpdateCreate(commodity_id=self.commodity.id, market_id=self.market.id,
                    price_low=90, price_high=110, unit="bag", bag_size="25 kg",
                    confidence_level="Admin confirmed", suggested_action="Watch", update_date_time=self.when)
        self.assertIsNone(payload.average_price)
        response = self.client.get(f"/price-updates/{current.id}")
        self.assertIsNone(response.json()["average_price"])

    def test_clearing_unsubstantiated_average_retains_original_and_updates_movement(self):
        first = self.approved(average_price=95)
        successor = self.approved(average_price=100, update_date_time=self.when + timedelta(hours=1))
        update_price_update(self.db, first, PriceUpdateUpdate(average_price=None,
                            correction_reason="Removed unsubstantiated synthetic average"), actor=self.admin)
        self.db.refresh(successor)
        self.assertIsNone(first.average_price)
        self.assertEqual(successor.movement, "unknown")
        revision = self.db.scalar(select(PriceRevision).where(PriceRevision.price_update_id == first.id))
        self.assertEqual(revision.original_values["average_price"], "95.00")

    def test_backfill_and_correction_recalculate_successor_with_evidence(self):
        first = self.approved(average_price=95)
        last = self.approved(average_price=100, update_date_time=self.when + timedelta(hours=2))
        middle = self.approved(average_price=105, update_date_time=self.when + timedelta(hours=1))
        self.db.refresh(last)
        self.assertEqual(last.previous_price_update_id, middle.id)
        self.assertEqual(last.movement, "down")
        update_price_update(self.db, middle, PriceUpdateUpdate(average_price=90, possible_meaning=None,
                            correction_reason="Synthetic corrected observation"), actor=self.admin)
        self.db.refresh(last)
        self.assertEqual(last.movement, "up")
        revision = self.db.scalar(select(PriceRevision).where(PriceRevision.price_update_id == middle.id))
        self.assertEqual(revision.original_values["average_price"], "105.00")
        self.assertIsNone(middle.possible_meaning)
        self.assertEqual(first.average_price, Decimal("95.00"))

    def test_legacy_unspecified_bags_never_become_comparable_or_public_history(self):
        old = self.approved()
        old.bag_size = None
        latest = self.approved(update_date_time=self.when + timedelta(hours=1))
        latest.bag_size = None
        self.db.commit()
        approve_price_update(self.db, latest, self.admin)
        self.assertEqual(self.client.get(f"/price-updates/{old.id}").status_code, 404)
        self.assertEqual(self.client.get(f"/price-updates/{latest.id}").status_code, 200)
        self.assertEqual(latest.measurement_status, "legacy_unspecified")
        self.assertNotEqual(old.measurement_series, latest.measurement_series)

    def test_lagos_calendar_day_bounds_include_midnight(self):
        inside = self.approved(update_date_time=datetime(2026, 1, 9, 23, 30, tzinfo=timezone.utc))
        outside = self.approved(bag_size="100 kg", update_date_time=datetime(2026, 1, 10, 23, tzinfo=timezone.utc))
        start, end = lagos_day_bounds(date(2026, 1, 10))
        self.assertEqual(start, datetime(2026, 1, 9, 23, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 1, 10, 23, tzinfo=timezone.utc))
        self.assertEqual([item.id for item in list_price_history(self.db, selected_date=date(2026, 1, 10))], [inside.id])
        self.assertNotEqual(inside.id, outside.id)

    def test_naive_and_future_times_are_rejected_and_offsets_normalized(self):
        for value in (datetime(2026, 1, 1), datetime.now(timezone.utc) + timedelta(minutes=6)):
            with self.assertRaises(ValidationError):
                PriceUpdateUpdate(update_date_time=value)
        accepted = PriceUpdateUpdate(update_date_time=datetime(2026, 1, 1, 1, tzinfo=timezone(timedelta(hours=1))))
        self.assertEqual(accepted.update_date_time, datetime(2026, 1, 1, tzinfo=timezone.utc))

    def test_public_and_free_responses_exclude_guidance_and_sources(self):
        price = self.approved()
        for reader in (None, self.free):
            self.reader = reader
            for path in ("/price-updates", f"/price-updates/{price.id}", f"/price-updates/comparison?commodity_id={self.commodity.id}"):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                item = response.json()[0] if isinstance(response.json(), list) else response.json()
                for field in ("possible_meaning", "suggested_action", "notes", "source_1", "source_2"):
                    self.assertNotIn(field, item)
                self.assertEqual(item["previous_price_low"], None)

    def test_trial_reads_full_fields_and_historical_ids(self):
        old = self.approved()
        self.approved(update_date_time=self.when + timedelta(hours=1))
        self.reader = self.trial
        response = self.client.get(f"/price-updates/{old.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["possible_meaning"], "Synthetic premium meaning")
        self.assertNotIn("source_1", response.json())
        self.assertEqual(self.client.get("/price-updates/history").status_code, 200)

    def test_price_list_checks_entitlement_once_for_all_records(self):
        for size in ("25 kg", "50 kg", "100 kg"):
            self.approved(bag_size=size)
        self.reader = self.trial
        from app.utils import permissions
        with patch.object(permissions, "find_subscription_for_user", wraps=permissions.find_subscription_for_user) as lookup:
            response = self.client.get("/price-updates")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(lookup.call_count, 1)

    def test_alternate_date_paths_and_direct_history_are_blocked_for_limited(self):
        old = self.approved()
        self.approved(update_date_time=self.when + timedelta(hours=1))
        for reader in (None, self.free):
            self.reader = reader
            self.assertEqual(self.client.get("/price-updates?date=2026-01-10").status_code, 403)
            self.assertEqual(self.client.get(f"/price-updates/comparison?commodity_id={self.commodity.id}&date=2026-01-10").status_code, 403)
            self.assertEqual(self.client.get(f"/price-updates/{old.id}").status_code, 404)
            self.assertIn(self.client.get("/price-updates/history").status_code, (401, 403))

    def test_inactive_references_hide_consumer_history_not_admin_evidence(self):
        price = self.approved()
        self.market.is_active = False
        self.db.commit()
        self.assertEqual(list_price_history(self.db), [])
        self.reader = self.admin
        self.assertEqual(self.client.get("/price-updates/admin/history").json()[0]["id"], price.id)

    def test_history_and_admin_pagination_are_bounded_and_stable(self):
        prices = [self.approved(update_date_time=self.when + timedelta(hours=i)) for i in range(3)]
        self.reader = self.admin
        first = self.client.get("/price-updates/history?page=1&page_size=2").json()
        second = self.client.get("/price-updates/history?page=2&page_size=2").json()
        self.assertEqual([item["id"] for item in first + second], [item.id for item in prices])
        self.assertEqual(self.client.get("/price-updates/history?page_size=1001").status_code, 422)
        self.assertEqual(len(self.client.get("/price-updates/admin/history?page_size=1").json()), 1)

    def test_distinct_sources_required_and_reporters_cannot_self_attest(self):
        with self.assertRaises(HTTPException):
            self.make_price(confidence_level="Verified by 2 sources", source_1=" Same ", source_2="same")
        self.admin.role = "reporter"
        submitted = self.make_price(confidence_level="Verified by 2 sources", source_1="same", source_2="same")
        self.assertEqual(submitted.confidence_level, "Reporter submitted")
        self.assertIsNone(submitted.source_1)

    def test_scope_change_with_linked_intelligence_is_rejected(self):
        price = self.approved()
        self.db.add(MarketSignal(commodity_id=self.commodity.id, market_id=self.market.id, price_update_id=price.id,
                               signal_type="Synthetic", signal_description="Synthetic observation", created_by=self.admin.id))
        self.db.commit()
        with self.assertRaises(HTTPException) as error:
            update_price_update(self.db, price, PriceUpdateUpdate(bag_size="100 kg"), actor=self.admin)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(price.bag_size, "50 kg")

    def test_withdrawal_retains_price_revision_and_links(self):
        price = self.approved()
        signal = MarketSignal(commodity_id=self.commodity.id, market_id=self.market.id, price_update_id=price.id,
                             signal_type="Synthetic", signal_description="Synthetic observation", created_by=self.admin.id)
        self.db.add(signal)
        self.db.commit()
        delete_price_update(self.db, price, actor=self.admin)
        self.assertEqual(self.db.get(PriceUpdate, price.id).status, "withdrawn")
        self.assertIsNotNone(self.db.get(MarketSignal, signal.id))
        self.assertIsNotNone(self.db.scalar(select(PriceRevision).where(PriceRevision.price_update_id == price.id)))
        self.assertEqual(list_price_history(self.db), [])

    def test_market_identity_database_constraint_and_namesake_markets(self):
        self.db.add(Market(name=" synthetic market ", state="SYNTHETIC STATE"))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()
        other = Market(name="Synthetic Market", state="Other synthetic state")
        self.db.add(other)
        self.db.commit()
        price = self.approved(market_id=other.id)
        self.assertEqual([item.id for item in list_latest_approved_price_updates(self.db, market_id=other.id)], [price.id])

    def test_cost_measurement_persists_and_null_cost_patch_is_controlled(self):
        cost = create_cost_breakdown(self.db, CostBreakdownCreate(commodity_id=self.commodity.id, market_id=self.market.id,
                    unit="bag", bag_size="50 kg", reference_date_time=self.when, purchase_price_reference=100, transport=10))
        self.assertEqual(cost.total_estimated_landing_storage_cost, Decimal("110.00"))
        self.approved(bag_size="100 kg")
        self.assertEqual(cost.bag_size, "50 kg")
        with self.assertRaises(HTTPException) as error:
            update_cost_breakdown(self.db, cost, CostBreakdownUpdate(transport=None))
        self.assertEqual(error.exception.status_code, 422)

    def test_approved_corrections_require_reason_and_append_restricted_original(self):
        price = self.approved()
        with self.assertRaises(HTTPException) as error:
            update_price_update(self.db, price, PriceUpdateUpdate(notes="Corrected synthetic note"), actor=self.admin)
        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(price.notes, "Synthetic premium note")
        update_price_update(self.db, price, PriceUpdateUpdate(notes=None, correction_reason="Cleared incorrect synthetic note"), actor=self.admin)
        revision = self.db.scalar(select(PriceRevision).where(PriceRevision.price_update_id == price.id))
        self.assertEqual(revision.original_values["notes"], "Synthetic premium note")
        self.assertIsNone(price.notes)

    def test_backdated_timestamp_correction_never_selects_itself_as_predecessor(self):
        first = self.approved()
        second = self.approved(update_date_time=self.when + timedelta(hours=1))
        update_price_update(self.db, first, PriceUpdateUpdate(update_date_time=self.when + timedelta(hours=2),
                            correction_reason="Corrected synthetic observation time"), actor=self.admin)
        self.assertEqual(first.previous_price_update_id, second.id)
        self.assertNotEqual(first.previous_price_update_id, first.id)

    def test_archiving_intelligence_retains_records_and_hides_them_from_reads(self):
        signal = MarketSignal(commodity_id=self.commodity.id, market_id=self.market.id, signal_type="Synthetic",
                              signal_description="Synthetic observation", created_by=self.admin.id)
        self.db.add(signal)
        self.db.commit()
        delete_market_signal(self.db, signal)
        self.assertIsNotNone(self.db.get(MarketSignal, signal.id))
        self.assertEqual(list_intelligence(self.db, MarketSignal), [])
        cost = create_cost_breakdown(self.db, CostBreakdownCreate(commodity_id=self.commodity.id, market_id=self.market.id,
                    unit="bag", bag_size="50 kg", reference_date_time=self.when, purchase_price_reference=100))
        delete_cost_breakdown(self.db, cost)
        self.assertIsNotNone(self.db.get(CostBreakdown, cost.id))
        self.assertEqual(list_intelligence(self.db, CostBreakdown), [])

    def test_current_query_materializes_latest_only_with_constant_query_count(self):
        self.db.add_all([PriceUpdate(commodity_id=self.commodity.id, market_id=self.market.id,
                        price_low=90, price_high=110, average_price=100, unit="bag", bag_size="50 kg", grade="A",
                        update_date_time=self.when + timedelta(minutes=i), status="approved", movement="stable",
                        confidence_level="Admin confirmed", created_by=self.admin.id, approved_by=self.admin.id)
                        for i in range(500)])
        self.db.commit()
        statements = []

        def collect(connection, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(statement)

        event.listen(self.engine, "before_cursor_execute", collect)
        try:
            current = list_latest_approved_price_updates(self.db)
        finally:
            event.remove(self.engine, "before_cursor_execute", collect)
        self.assertEqual(len(current), 1)
        self.assertEqual(len(statements), 3)  # current + two select-in reference loads
        self.assertIn("row_number() OVER", statements[0])
        self.assertEqual(count_latest_approved_price_updates(self.db), 1)

    def test_csv_neutralizes_text_formulas_without_changing_decimal_values(self):
        price = self.approved()
        price.commodity.name = " =HYPERLINK(\"https://reserved.invalid\")"
        price.notes = "Synthetic ordinary note"
        price.possible_meaning = "@SUM(1,2)"
        row = list(csv.DictReader(StringIO(build_price_report_csv([price]))))[0]
        self.assertTrue(row["commodity"].startswith("'"))
        self.assertTrue(row["possible_meaning"].startswith("'"))
        self.assertEqual(row["price_low"], "90.00")
        self.assertEqual(row["bag_size"], "50 kg")
        self.assertEqual(spreadsheet_safe_text("ordinary"), "ordinary")

    def test_basic_signal_omits_guidance_and_quality_is_premium(self):
        self.db.add(MarketSignal(commodity_id=self.commodity.id, market_id=self.market.id, signal_type="Synthetic",
                    signal_description="Synthetic basic observation", possible_meaning="Synthetic deeper meaning",
                    suggested_action="Watch", created_by=self.admin.id))
        self.db.commit()
        self.reader = self.free
        item = self.client.get(f"/market-signals?commodity_id={self.commodity.id}").json()[0]
        self.assertNotIn("possible_meaning", item)
        self.assertNotIn("suggested_action", item)
        self.assertEqual(self.client.get("/quality-signals").status_code, 403)
        self.reader = self.trial
        self.assertIn("possible_meaning", self.client.get("/market-signals").json()[0])

    def test_buying_zone_one_bound_freshness_is_explicit_without_hiding(self):
        zone = BuyingZone(commodity_id=self.commodity.id, market_id=self.market.id, price_low=90, price_high=100,
                          reason="Synthetic", confidence="Synthetic", created_by=self.admin.id,
                          valid_to=date(2025, 1, 1))
        self.assertEqual(zone.validity_status, "expired")


if __name__ == "__main__":
    unittest.main()
