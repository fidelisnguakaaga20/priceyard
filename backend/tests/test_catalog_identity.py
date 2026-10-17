from datetime import datetime, timezone
import threading
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.commodity_schema import CommodityCreate, CommodityUpdate
from app.schemas.market_schema import MarketCreate, MarketUpdate
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.commodity_service import create_commodity, get_commodity, update_commodity
from app.services.market_service import create_market, get_market, update_market


def verify_catalog_races(check, engine, *, first_commits):
    """Two application writers, deterministic lock overlap, no native suite overlap."""
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic catalog race owner", email="catalog-race@example.com",
                     password_hash="unused", role="admin", referral_code="CATRACE")
        commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
        db.add_all([owner, commodity, market])
        db.flush()
        owner_id = owner.id
        db.add(PriceUpdate(commodity_id=commodity.id, market_id=market.id, unit="1 bag",
            price_low=210000, price_high=220000, movement="unknown", confidence_level="Low confidence",
            status="approved", created_by=owner.id, update_date_time=datetime.now(timezone.utc),
            source_1="PRIVATE-CATALOG-HISTORY"))
        db.commit()
        original_history = db.execute(select(PriceUpdate.__table__)).all()

    for kind, model, create, update, get, create_schema, update_schema in (
        ("commodity", Commodity, create_commodity, update_commodity, get_commodity, CommodityCreate, CommodityUpdate),
        ("market", Market, create_market, update_market, get_market, MarketCreate, MarketUpdate),
    ):
        for contender_edits in (False, True):
            name = f"Synthetic {kind} identity {'rename' if contender_edits else 'create'}"
            target_id = None
            if contender_edits:
                with Session(engine) as db:
                    target = model(name="Original " + name, description="Keep this saved description")
                    db.add(target)
                    db.commit()
                    target_id = target.id
            ready, attempted, release, finished = (threading.Event() for _ in range(4))
            results = {}

            def observe(connection, cursor, statement, parameters, context, many):
                if threading.current_thread().name == "catalog-contender" and (
                    "pg_advisory_xact_lock" in statement or "lower(" in statement.lower()
                ):
                    attempted.set()

            def save_audit(db, item, action):
                create_audit_log(db, actor=db.get(User, owner_id), action=kind + action,
                    table_name=model.__tablename__, record_id=item.id, new_value=snapshot_model(item), commit=False)

            def first_writer():
                try:
                    with Session(engine) as db:
                        item = create(db, create_schema(name=name), commit=False)
                        save_audit(db, item, ".create")
                        ready.set()
                        if not release.wait(10):
                            raise RuntimeError("Synthetic release timed out")
                        db.commit() if first_commits else db.rollback()
                        results["first"] = "committed" if first_commits else "rolled_back"
                except Exception as error:
                    results["first"] = type(error).__name__

            def second_writer():
                try:
                    if not ready.wait(10):
                        raise RuntimeError("Synthetic first writer timed out")
                    with Session(engine) as db:
                        try:
                            if contender_edits:
                                item = update(db, get(db, target_id, lock=True), update_schema(name=name.swapcase()), commit=False)
                            else:
                                item = create(db, create_schema(name=name.swapcase()), commit=False)
                            save_audit(db, item, ".edit" if contender_edits else ".create")
                            db.commit()
                            results["second"] = "saved"
                        except HTTPException as error:
                            db.rollback()
                            results["second"] = error.status_code
                except Exception as error:
                    results["second"] = type(error).__name__
                finally:
                    finished.set()

            event.listen(engine, "before_cursor_execute", observe)
            workers = [threading.Thread(target=first_writer, name="catalog-first"),
                       threading.Thread(target=second_writer, name="catalog-contender")]
            try:
                for worker in workers:
                    worker.start()
                check.assertTrue(attempted.wait(5))
                check.assertFalse(finished.wait(0.15), "Contender must wait for the first audited transaction")
            finally:
                release.set()
                for worker in workers:
                    worker.join(12)
                event.remove(engine, "before_cursor_execute", observe)
            check.assertFalse(any(worker.is_alive() for worker in workers))
            check.assertEqual(results, {"first": "committed" if first_commits else "rolled_back",
                                        "second": 409 if first_commits else "saved"})
            with Session(engine) as db:
                matches = [item for item in db.scalars(select(model)) if item.name.lower() == name.lower()]
                check.assertEqual(len(matches), 1)
                if contender_edits:
                    original = db.get(model, target_id)
                    check.assertEqual(original.description, "Keep this saved description")
                    check.assertEqual(original.name, "Original " + name if first_commits else name.swapcase())
                check.assertEqual(db.execute(select(PriceUpdate.__table__)).all(), original_history)
    with Session(engine) as db:
        check.assertEqual(len(db.scalars(select(AuditLog)).all()), 4)


class CatalogIdentityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_commodity_case_and_whitespace_duplicate_keeps_original(self):
        with Session(self.engine) as db:
            item = create_commodity(db, CommodityCreate(name="Egusi", description="Original"))
            original = snapshot_model(item)
            with self.assertRaises(HTTPException) as error:
                create_commodity(db, CommodityCreate(name="  eGUSI  "))
            self.assertEqual(error.exception.status_code, 409)
            db.rollback()
            self.assertEqual(snapshot_model(db.get(Commodity, item.id)), original)
            self.assertEqual(len(db.scalars(select(Commodity)).all()), 1)

    def test_commodity_rename_collision_preserves_ids_and_metadata(self):
        with Session(self.engine) as db:
            create_commodity(db, CommodityCreate(name="Egusi"))
            target = create_commodity(db, CommodityCreate(name="Honey Beans", description="Saved"))
            before = snapshot_model(target)
            with self.assertRaises(HTTPException) as error:
                update_commodity(db, target, CommodityUpdate(name="EGUSI", description="Must not save"))
            self.assertEqual(error.exception.status_code, 409)
            db.rollback()
            self.assertEqual(snapshot_model(db.get(Commodity, target.id)), before)

    def test_market_state_case_whitespace_and_null_duplicate_rules_unchanged(self):
        with Session(self.engine) as db:
            for state in (None, "FCT"):
                item = create_market(db, MarketCreate(name="Kwali Market", state=state))
                for requested in ((None, "") if state is None else ("fct", " FCT ")):
                    with self.assertRaises(HTTPException) as error:
                        create_market(db, MarketCreate(name=" kWALI mARKET ", state=requested))
                    self.assertEqual(error.exception.status_code, 409)
                    db.rollback()
                self.assertEqual(db.get(Market, item.id).state, state)
            self.assertEqual(len(db.scalars(select(Market)).all()), 2)

    def test_market_rename_and_state_collision_preserve_saved_record(self):
        with Session(self.engine) as db:
            create_market(db, MarketCreate(name="Kwali Market", state="FCT"))
            target = create_market(db, MarketCreate(name="Kwali Market", state="Benue", description="Original"))
            before = snapshot_model(target)
            with self.assertRaises(HTTPException) as error:
                update_market(db, target, MarketUpdate(state=" fct ", description="Must not save"))
            self.assertEqual(error.exception.status_code, 409)
            db.rollback()
            self.assertEqual(snapshot_model(db.get(Market, target.id)), before)

    def test_legacy_duplicate_records_are_not_merged_or_renamed(self):
        with Session(self.engine) as db:
            db.add_all([Commodity(name="Egusi", description="First evidence"),
                        Commodity(name="EGUSI", description="Second evidence")])
            db.commit()
            before = db.execute(select(Commodity.__table__).order_by(Commodity.id)).all()
            with self.assertRaises(HTTPException):
                create_commodity(db, CommodityCreate(name="egusi"))
            db.rollback()
            self.assertEqual(db.execute(select(Commodity.__table__).order_by(Commodity.id)).all(), before)
