from datetime import datetime, timezone
import threading
import unittest

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.market_signal import MarketSignal
from app.models.price_update import PriceUpdate
from app.models.quality_signal import QualitySignal
from app.models.storage_suitability import StorageSuitability
from app.models.user import User
from app.schemas.market_signal_schema import MarketSignalCreate
from app.schemas.price_update_schema import PriceUpdateUpdate
from app.schemas.quality_signal_schema import QualitySignalCreate
from app.schemas.storage_suitability_schema import StorageSuitabilityCreate
from app.security import create_access_token
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.market_signal_service import create_market_signal
from app.services.price_update_service import get_price_update_for_admin, update_price_update
from app.services.quality_signal_service import create_quality_signal
from app.services.storage_suitability_service import create_storage_suitability


RESOURCES = (
    (MarketSignal, MarketSignalCreate, create_market_signal, {"signal_type": "Synthetic", "signal_description": "Saved observation"}),
    (QualitySignal, QualitySignalCreate, create_quality_signal, {"quality_status": "Saved observation"}),
    (StorageSuitability, StorageSuitabilityCreate, create_storage_suitability, {"suitability_status": "good"}),
)


def seed_scope(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic scope owner", email="scope-owner@example.com", password_hash="unused", role="admin", referral_code="PRICESCOPE")
        commodities = [Commodity(name="Egusi"), Commodity(name="Honey Beans")]
        markets = [Market(name="Kwali Market"), Market(name="Synthetic scope fixture")]
        db.add_all([owner, *commodities, *markets])
        db.commit()
        return owner.id, commodities[0].id, commodities[1].id, markets[0].id, markets[1].id


def new_price(db, owner_id, commodity_id, market_id):
    price = PriceUpdate(commodity_id=commodity_id, market_id=market_id, unit="1 bag", bag_size=None,
        price_low=210000, price_high=220000, movement="unknown", confidence_level="Low confidence",
        status="approved", created_by=owner_id, update_date_time=datetime.now(timezone.utc), source_1="PRIVATE-SCOPE-EVIDENCE")
    db.add(price)
    db.commit()
    return price.id


def attach(db, resource, owner_id, price_id, commodity_id, market_id):
    model, schema, create, fields = resource
    payload = schema(price_update_id=price_id, commodity_id=commodity_id, market_id=market_id, **fields)
    return create(db, payload, commit=False) if model is StorageSuitability else create(db, payload, db.get(User, owner_id), commit=False)


def verify_scope_races(check, engine):
    owner_id, commodity_id, other_id, market_id, _ = seed_scope(engine)
    for resource in RESOURCES:
        model = resource[0]
        for child_first in (True, False):
            with Session(engine) as db:
                price_id = new_price(db, owner_id, commodity_id, market_id)
            ready, attempted, release, finished = (threading.Event() for _ in range(4))
            results = {}

            def observe(connection, cursor, statement, parameters, context, many):
                if threading.current_thread().name == "scope-contender" and "FOR UPDATE" in statement.upper():
                    attempted.set()

            def apply(db, make_child):
                if make_child:
                    item = attach(db, resource, owner_id, price_id, commodity_id, market_id)
                else:
                    item = update_price_update(db, get_price_update_for_admin(db, price_id, lock=True),
                                               PriceUpdateUpdate(commodity_id=other_id), commit=False)
                create_audit_log(db, actor=db.get(User, owner_id), action="synthetic.scope", table_name=item.__tablename__,
                                 record_id=item.id, new_value=snapshot_model(item), commit=False)

            def first_writer():
                try:
                    with Session(engine) as db:
                        apply(db, child_first)
                        ready.set()
                        if not release.wait(10):
                            raise RuntimeError("Synthetic scope release timed out")
                        db.commit()
                        results["first"] = "saved"
                except Exception as error:
                    results["first"] = type(error).__name__

            def contender():
                try:
                    if not ready.wait(10):
                        raise RuntimeError("Synthetic scope first writer timed out")
                    with Session(engine) as db:
                        try:
                            apply(db, not child_first)
                            db.commit()
                            results["second"] = "saved"
                        except HTTPException as error:
                            db.rollback()
                            results["second"] = error.status_code
                except Exception as error:
                    results["second"] = type(error).__name__
                finally:
                    finished.set()

            workers = [threading.Thread(target=first_writer, name="scope-first"), threading.Thread(target=contender, name="scope-contender")]
            event.listen(engine, "before_cursor_execute", observe)
            try:
                for worker in workers:
                    worker.start()
                check.assertTrue(attempted.wait(5))
                check.assertFalse(finished.wait(0.1))
            finally:
                release.set()
                for worker in workers:
                    worker.join(12)
                event.remove(engine, "before_cursor_execute", observe)
            check.assertFalse(any(worker.is_alive() for worker in workers))
            check.assertEqual(results, {"first": "saved", "second": 409 if child_first else 422})
            with Session(engine) as db:
                price = db.get(PriceUpdate, price_id)
                linked = db.scalars(select(model).where(model.price_update_id == price_id)).all()
                check.assertEqual(price.commodity_id, commodity_id if child_first else other_id)
                check.assertEqual(len(linked), 1 if child_first else 0)
                check.assertTrue(all((row.commodity_id, row.market_id) == (price.commodity_id, price.market_id) for row in linked))
                check.assertEqual(price.source_1, "PRIVATE-SCOPE-EVIDENCE")
    with Session(engine) as db:
        check.assertEqual(len(db.scalars(select(AuditLog)).all()), 6)


class PriceScopeTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        self.owner_id, self.commodity_id, self.other_id, self.market_id, self.other_market_id = seed_scope(self.engine)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def check_linked_move(self, field, destination):
        for resource in RESOURCES:
            with self.subTest(model=resource[0].__name__), Session(self.engine) as db:
                price_id = new_price(db, self.owner_id, self.commodity_id, self.market_id)
                attach(db, resource, self.owner_id, price_id, self.commodity_id, self.market_id)
                db.commit()
                before = db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all()
                with self.assertRaises(HTTPException) as error:
                    update_price_update(db, db.get(PriceUpdate, price_id), PriceUpdateUpdate(**{field: destination}))
                self.assertEqual(error.exception.status_code, 409)
                db.rollback()
                self.assertEqual(db.execute(select(PriceUpdate.__table__).order_by(PriceUpdate.id)).all(), before)

    def test_linked_commodity_correction_cannot_strand_saved_observations(self):
        self.check_linked_move("commodity_id", self.other_id)

    def test_linked_market_correction_cannot_strand_saved_observations(self):
        self.check_linked_move("market_id", self.other_market_id)

    def test_unlinked_correction_preserves_price_id_fields_and_source(self):
        with Session(self.engine) as db:
            price_id = new_price(db, self.owner_id, self.commodity_id, self.market_id)
            item = update_price_update(db, get_price_update_for_admin(db, price_id),
                                      PriceUpdateUpdate(commodity_id=self.other_id, market_id=self.other_market_id))
            self.assertEqual((item.id, item.commodity.id, item.market.id), (price_id, self.other_id, self.other_market_id))
            self.assertEqual(item.source_1, "PRIVATE-SCOPE-EVIDENCE")
            self.assertEqual(item.unit, "1 bag")
            self.assertIsNone(item.bag_size)

    def test_valid_price_edit_with_saved_links_still_works(self):
        with Session(self.engine) as db:
            price_id = new_price(db, self.owner_id, self.commodity_id, self.market_id)
            for resource in RESOURCES:
                attach(db, resource, self.owner_id, price_id, self.commodity_id, self.market_id)
            db.commit()
            item = update_price_update(db, db.get(PriceUpdate, price_id), PriceUpdateUpdate(
                commodity_id=self.commodity_id, market_id=self.market_id, price_low=211000))
            self.assertEqual(item.price_low, 211000)
            for resource in RESOURCES:
                self.assertEqual(db.scalar(select(resource[0])).price_update_id, price_id)

    def test_new_link_after_correction_rejects_old_scope_without_rewriting_price(self):
        with Session(self.engine) as db:
            price_id = new_price(db, self.owner_id, self.commodity_id, self.market_id)
            update_price_update(db, db.get(PriceUpdate, price_id), PriceUpdateUpdate(commodity_id=self.other_id))
            for resource in RESOURCES:
                with self.assertRaises(HTTPException) as error:
                    attach(db, resource, self.owner_id, price_id, self.commodity_id, self.market_id)
                self.assertEqual(error.exception.status_code, 422)
                db.rollback()
                self.assertIsNone(db.scalar(select(resource[0])))
            self.assertEqual(db.get(PriceUpdate, price_id).commodity_id, self.other_id)

    def test_rejected_http_correction_preserves_price_observation_and_audit(self):
        with Session(self.engine) as db:
            price_id = new_price(db, self.owner_id, self.commodity_id, self.market_id)
            attach(db, RESOURCES[0], self.owner_id, price_id, self.commodity_id, self.market_id)
            db.commit()
            before = {model.__tablename__: db.execute(select(model.__table__)).all() for model in (PriceUpdate, MarketSignal, AuditLog)}
        def sessions():
            with Session(self.engine) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        with TestClient(app) as client:
            response = client.patch(f"/price-updates/{price_id}", json={"commodity_id": self.other_id},
                headers={"Authorization": "Bearer " + create_access_token(user_id=self.owner_id)})
            self.assertEqual(response.status_code, 409)
            self.assertNotIn("PRIVATE", response.text)
        with Session(self.engine) as db:
            self.assertEqual({model.__tablename__: db.execute(select(model.__table__)).all() for model in (PriceUpdate, MarketSignal, AuditLog)}, before)
