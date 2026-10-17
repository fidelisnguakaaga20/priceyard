"""Only the freshly marked local cluster; guard before any application import."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[1]
sys.path.insert(0, str(LAB))
marker = json.loads((LAB / "runtime/postgres-marker.json").read_text(encoding="utf-8-sig"))
EXPECTED_DIR = (LAB / "runtime/postgres-revocation").resolve()
if (Path(marker["data_directory"]).resolve() != EXPECTED_DIR or marker["system_identifier"] != "7697280512362447984"
        or marker["host"] != "127.0.0.1" or marker["port"] != 55447 or marker["user"] != "priceyard_revocation_test"
        or marker["database"] != "priceyard_isolated_test" or marker["purpose"] != "new-synthetic-only-security-migration"):
    raise RuntimeError("Unapproved PostgreSQL identity marker")

import sqlalchemy
import psycopg
from psycopg.conninfo import conninfo_to_dict
original_engine = sqlalchemy.create_engine
original_connect = psycopg.Connection.connect
import guard
guard.isolate()
import os
URL = "postgresql+psycopg://priceyard_revocation_test@127.0.0.1:55447/priceyard_isolated_test"
os.environ["DATABASE_URL"] = URL
os.environ["PGPASSFILE"] = str(LAB / "runtime/nonexistent-synthetic-passfile")
os.environ["PGSERVICEFILE"] = str(LAB / "runtime/nonexistent-synthetic-services")
CURRENT_SCHEMA = None


def pinned_connect(conninfo="", **kwargs):
    if "context" in kwargs and not isinstance(kwargs["context"], psycopg.adapt.AdaptersMap):
        raise RuntimeError("Unsupported PostgreSQL adapter context")
    connect_values = {key: value for key, value in kwargs.items() if key not in {"autocommit", "context"}}
    info = conninfo_to_dict(conninfo, **connect_values)
    if (set(info) - {"host", "port", "user", "dbname", "connect_timeout", "application_name", "sslmode"}
            or info.get("host") != "127.0.0.1" or str(info.get("port")) != "55447"
            or info.get("user") != marker["user"] or info.get("dbname") not in {"postgres", marker["database"]}
            or info.get("sslmode") not in {None, "disable"}):
        raise RuntimeError("Only the marked local synthetic PostgreSQL connection is permitted: " + repr({"keys": sorted(info), "host_matches": info.get("host") == "127.0.0.1", "port_matches": str(info.get("port")) == "55447", "user_matches": info.get("user") == marker["user"], "database_matches": info.get("dbname") in {"postgres", marker["database"]}}))
    # Literal loopback fixture only: no certificate/key discovery or hanging DNS.
    kwargs.update(sslmode="disable", connect_timeout=5)
    connection = original_connect(conninfo, **kwargs)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_setting('data_directory'), system_identifier::text FROM pg_control_system()")
            data_directory, identifier = cursor.fetchone()
        if Path(data_directory).resolve() != EXPECTED_DIR or identifier != marker["system_identifier"]:
            raise RuntimeError("Live server identity differs; no mutations permitted")
        if not connection.autocommit:
            connection.rollback()
        return connection
    except BaseException:
        connection.close()
        raise


psycopg.connect = pinned_connect
psycopg.Connection.connect = pinned_connect


def pinned_engine(url, *args, **kwargs):
    if str(url) != URL or "creator" in kwargs or kwargs.get("connect_args"):
        raise RuntimeError("Only the literal marked test URL is permitted")
    engine = original_engine(url, *args, **kwargs)
    if CURRENT_SCHEMA:
        schema = CURRENT_SCHEMA
        @sqlalchemy.event.listens_for(engine, "connect")
        def set_schema(connection, record):
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO "'+schema+'"')
            connection.commit()
    return engine


sqlalchemy.create_engine = pinned_engine
sqlalchemy.engine.create_engine = pinned_engine
importlib.import_module("sqlalchemy.engine.create").create_engine = pinned_engine

# Identity verification above precedes every connection, including this database
# creation. Never choose or mutate an existing arbitrary application database.
with pinned_connect(host="127.0.0.1", port=55447, user=marker["user"], dbname="postgres", autocommit=True) as connection:
    exists = connection.execute("SELECT 1 FROM pg_database WHERE datname = %s", (marker["database"],)).fetchone()
    if not exists:
        connection.execute('CREATE DATABASE "priceyard_isolated_test"')

import hashlib
import threading
import time
import unittest
from unittest.mock import patch
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from alembic import command
from alembic.config import Config
from fastapi import HTTPException
from sqlalchemy import text, select
from sqlalchemy.orm import Session
from app.database import Base
import app.models
from app.models.password_reset_token import PasswordResetToken
from app.models.revoked_access_token import RevokedAccessToken
from app.models.user import User
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.models.push_subscription import PushSubscription
from app.schemas.push_schema import PushSubscriptionCreate
from app.security import create_access_token
from app.services import password_reset_service
from app.services import payment_service
from app.services.auth_service import register_user
from app.schemas.auth_schema import RegisterRequest
from app.services.push_service import save_subscription
from app.services.login_revocation_service import is_revoked, revoke_token
from app.services.subscription_service import build_trial_subscription, update_subscription_status
from app.models.subscription import Subscription
from app.services.user_service import update_user
from app.schemas.user_schema import AdminUserUpdate
from app.utils.password import hash_password


class PostgreSQLSecurityTests(unittest.TestCase):
    def test_current_price_specifications_preserve_variants_and_dashboard_history(self):
        from sqlalchemy import event
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.services.price_update_service import list_latest_approved_price_updates,list_price_history
        from app.services.admin_summary_service import get_admin_summary
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic specification admin",email="pg-spec@example.com",password_hash="unused",role="admin",referral_code="PGSPECS")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market");db.add_all([admin,commodity,market]);db.flush();ids=[]
            specs=[("recorded quantity one","recorded size one","recorded type one"),("recorded quantity two","recorded size one","recorded type one"),
                   ("recorded quantity one","recorded size two","recorded type one"),("recorded quantity one","recorded size one","recorded type two"),
                   (" RECORDED QUANTITY ONE "," RECORDED SIZE ONE "," RECORDED TYPE ONE ")]
            for index,(unit,size,kind) in enumerate(specs):
                item=PriceUpdate(commodity_id=commodity.id,market_id=market.id,unit=unit,bag_size=size,commodity_type=kind,price_low=210000,price_high=220000,
                    movement="unknown",confidence_level="Low confidence",status="approved",update_date_time=datetime.now(timezone.utc)+timedelta(minutes=index),created_by=admin.id)
                db.add(item);db.flush();ids.append(item.id)
            db.commit()
        with Session(self.engine) as db:
            before=db.execute(select(PriceUpdate.__table__)).all();loaded=[]
            event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(instance.id) if isinstance(instance,PriceUpdate) else None)
            self.assertEqual([row.id for row in list_latest_approved_price_updates(db)],list(reversed(ids[1:])))
            self.assertEqual(set(loaded),set(ids[1:]));self.assertEqual(get_admin_summary(db).latest,4)
            self.assertEqual(len(list_price_history(db)),5);self.assertEqual(db.execute(select(PriceUpdate.__table__)).all(),before)

    def test_flag_review_is_one_query_and_reason_matches_existing_storage_limit(self):
        from pydantic import ValidationError
        from sqlalchemy import event
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_flag import PriceFlag
        from app.models.price_update import PriceUpdate
        from app.schemas.price_flag_schema import PriceFlagCreate
        from app.services.price_flag_service import list_flagged_price_updates
        Base.metadata.create_all(self.engine)
        now=datetime.now(timezone.utc)
        with Session(self.engine) as db:
            users=[User(full_name="Synthetic flag query",email=f"pgflagq{i}@example.com",password_hash="unused",role="admin" if i==0 else "free_user",referral_code=f"PGFLAGQ{i}") for i in range(3)]
            commodity,market=Commodity(name="Egusi",is_active=False),Market(name="Kwali Market",is_active=False)
            db.add_all([*users,commodity,market]);db.flush()
            for age,state in ((2,"approved"),(1,"rejected"),(0,"pending")):
                price=PriceUpdate(commodity_id=commodity.id,market_id=market.id,unit="1 bag",bag_size=None,price_low=210000,price_high=220000,
                    movement="unknown",confidence_level="Low confidence",status=state,update_date_time=now-timedelta(days=age),created_by=users[0].id)
                db.add(price);db.flush()
                for index,user in enumerate(users):db.add(PriceFlag(price_update_id=price.id,user_id=user.id,reason=PriceFlagCreate(reason="é"*50).reason,resolved=index==2,created_at=now-timedelta(hours=age)))
            db.commit()
        with Session(self.engine) as db:
            tables=(PriceUpdate.__table__,PriceFlag.__table__);before={table.name:db.execute(select(table)).all() for table in tables};loaded=[];statements=[]
            event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(instance))
            def capture(connection,cursor,statement,parameters,context,many):statements.append(statement)
            event.listen(self.engine,"before_cursor_execute",capture);rows=list_flagged_price_updates(db);event.remove(self.engine,"before_cursor_execute",capture)
            self.assertEqual(len(rows),3);self.assertEqual([row.flag_count for row in rows],[2,2,2]);self.assertEqual(len(statements),1);self.assertEqual(loaded,[])
            with self.assertRaises(ValidationError):PriceFlagCreate(reason="é"*51)
            for table in tables:self.assertEqual(db.execute(select(table)).all(),before[table.name])

    def test_moderation_failure_preserves_private_feedback_price_and_flags(self):
        from app.models.commodity import Commodity
        from app.models.feedback import Feedback
        from app.models.market import Market
        from app.models.price_flag import PriceFlag
        from app.models.price_update import PriceUpdate
        from app.routes import feedback_routes,price_update_routes
        from app.schemas.feedback_schema import TestimonialPublishRequest
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic moderation admin",email="pg-moderation@example.com",password_hash="unused",role="admin",referral_code="PGMOD")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market");db.add_all([admin,commodity,market]);db.flush()
            feedback=Feedback(user_id=admin.id,rating=4,comment="Synthetic moderation feedback",screenshot_data="data:image/png;base64,c3ludGhldGlj")
            price=PriceUpdate(commodity_id=commodity.id,market_id=market.id,unit="1 bag",bag_size=None,price_low=210000,price_high=220000,
                movement="unknown",confidence_level="Low confidence",status="approved",update_date_time=datetime.now(timezone.utc),created_by=admin.id)
            db.add_all([feedback,price]);db.flush();db.add(PriceFlag(price_update_id=price.id,user_id=admin.id,reason="Synthetic private flag"));db.commit()
            admin_id,feedback_id,price_id=admin.id,feedback.id,price.id
        def snapshot(db):return {table.name:db.execute(select(table)).all() for table in (Feedback.__table__,PriceUpdate.__table__,PriceFlag.__table__,AuditLog.__table__)}
        for route,operation in ((feedback_routes,lambda db,admin:feedback_routes.publish_testimonial(feedback_id,TestimonialPublishRequest(display_name="Synthetic user"),db,admin)),
                                (feedback_routes,lambda db,admin:feedback_routes.remove_feedback(feedback_id,db,admin)),
                                (price_update_routes,lambda db,admin:price_update_routes.remove_price_update(price_id,db,admin)),
                                (price_update_routes,lambda db,admin:price_update_routes.resolve_price_flags(price_id,db,admin))):
            with Session(self.engine) as db:
                before=snapshot(db);admin=db.get(User,admin_id)
                with patch.object(route,"create_audit_log",side_effect=RuntimeError("Synthetic moderation audit failure")),self.assertRaisesRegex(RuntimeError,"Synthetic moderation audit failure"):
                    operation(db,admin)
                self.assertEqual(snapshot(db),before)
        barrier=threading.Barrier(2);outcomes=[]
        def worker():
            with Session(self.engine) as db:
                admin=db.get(User,admin_id);barrier.wait(timeout=15)
                try:price_update_routes.resolve_price_flags(price_id,db,admin);outcomes.append(204)
                except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
        threads=[threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads));self.assertEqual(outcomes,[204,204])
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog)).all();self.assertEqual(len(logs),1)
            self.assertEqual(logs[0].new_value,{"unresolved_count":0,"resolved_count":1});self.assertTrue(db.scalar(select(PriceFlag)).resolved)

    def test_concurrent_testimonial_moderation_keeps_private_image_and_continuous_audit(self):
        from app.models.feedback import Feedback
        from app.routes import feedback_routes
        from app.schemas.feedback_schema import TestimonialPublishRequest
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic testimonial admin",email="pg-testimonial@example.com",password_hash="unused",role="admin",referral_code="PGTESTIMONY")
            db.add(admin);db.flush();item=Feedback(user_id=admin.id,rating=4,comment="Synthetic feedback",screenshot_data="data:image/png;base64,c3ludGhldGlj")
            db.add(item);db.commit();admin_id,item_id=admin.id,item.id
        barrier=threading.Barrier(2);outcomes=[]
        def worker(publish):
            with Session(self.engine) as db:
                admin=db.get(User,admin_id);barrier.wait(timeout=15)
                try:
                    if publish:feedback_routes.publish_testimonial(item_id,TestimonialPublishRequest(display_name="Synthetic user"),db,admin)
                    else:feedback_routes.hide_testimonial(item_id,db,admin)
                    outcomes.append(200)
                except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
        threads=[threading.Thread(target=worker,args=(publish,)) for publish in (True,False)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads));self.assertEqual(outcomes,[200,200])
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog).order_by(AuditLog.id)).all();self.assertEqual(len(logs),2)
            self.assertEqual(logs[1].old_value,logs[0].new_value)
            self.assertNotIn("screenshot_data",str([(row.old_value,row.new_value) for row in logs]))
            self.assertEqual(db.get(Feedback,item_id).screenshot_data,"data:image/png;base64,c3ludGhldGlj")

    def test_catalog_audit_rollback_concurrent_edits_and_referenced_history_protection(self):
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.routes import commodity_routes, market_routes
        from app.schemas.commodity_schema import CommodityUpdate
        from app.schemas.market_schema import MarketUpdate
        from app.services.audit_service import snapshot_model
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic catalog admin",email="pg-catalog@example.com",password_hash="unused",role="admin",referral_code="PGCATALOG")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market")
            db.add_all([admin,commodity,market]);db.flush();admin_id,commodity_id,market_id=admin.id,commodity.id,market.id
            db.add(PriceUpdate(commodity_id=commodity.id,market_id=market.id,price_low=210000,price_high=220000,
                unit="1 bag",bag_size=None,movement="unknown",confidence_level="Low confidence",status="approved",
                update_date_time=datetime.now(timezone.utc),created_by=admin.id));db.commit()
            history_before=db.execute(select(PriceUpdate.__table__)).all()
        for kind,model,item_id,route,schema in (("commodity",Commodity,commodity_id,commodity_routes,CommodityUpdate),("market",Market,market_id,market_routes,MarketUpdate)):
            edit=getattr(route,'edit_'+kind)
            with Session(self.engine) as db:
                admin=db.get(User,admin_id);before=snapshot_model(db.get(model,item_id))
                with patch.object(route,"create_audit_log",side_effect=RuntimeError("Synthetic catalog audit failure")),self.assertRaisesRegex(RuntimeError,"Synthetic catalog audit failure"):
                    edit(item_id,schema(description="Synthetic failed edit",is_active=False),db,admin)
                self.assertEqual(snapshot_model(db.get(model,item_id)),before)
            barrier=threading.Barrier(2);outcomes=[]
            def worker(index):
                with Session(self.engine) as db:
                    admin=db.get(User,admin_id);barrier.wait(timeout=15)
                    try:edit(item_id,schema(description=f"Synthetic corrected description {index}"),db,admin);outcomes.append(200)
                    except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
            threads=[threading.Thread(target=worker,args=(index,)) for index in range(2)]
            for thread in threads:thread.start()
            for thread in threads:thread.join(25)
            self.assertFalse(any(thread.is_alive() for thread in threads));self.assertEqual(outcomes,[200,200])
            with Session(self.engine) as db:
                logs=db.scalars(select(AuditLog).where(AuditLog.action==kind+'.edit').order_by(AuditLog.id)).all()
                self.assertEqual(len(logs),2);self.assertEqual(logs[0].old_value,before)
                self.assertEqual(logs[1].old_value,logs[0].new_value);self.assertEqual(logs[1].new_value,snapshot_model(db.get(model,item_id)))
                admin=db.get(User,admin_id)
                with self.assertRaises(HTTPException) as failure:getattr(route,'remove_'+kind)(item_id,db,admin)
                self.assertEqual(failure.exception.status_code,409);self.assertIsNotNone(db.get(model,item_id))
                self.assertEqual(db.execute(select(PriceUpdate.__table__)).all(),history_before)
                self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action.like(kind+'.%'))).all()),2)

    def test_faq_failed_delete_and_concurrent_edits_preserve_record_and_audit(self):
        from app.models.faq_item import FAQItem
        from app.routes import faq_routes
        from app.schemas.faq_schema import FAQUpdate
        from app.services.audit_service import snapshot_model
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic FAQ admin",email="pg-faq@example.com",password_hash="unused",role="admin",referral_code="PGFAQ")
            db.add(admin);db.flush()
            item=FAQItem(question="Synthetic saved question",answer="Synthetic saved answer",category="Local testing",created_by=admin.id,is_published=False)
            db.add(item);db.commit();admin_id,item_id=admin.id,item.id;before=snapshot_model(item)
            with patch.object(faq_routes,"create_audit_log",side_effect=RuntimeError("Synthetic FAQ audit failure")),self.assertRaisesRegex(RuntimeError,"Synthetic FAQ audit failure"):
                faq_routes.remove_item(item_id,db,admin)
            self.assertEqual(snapshot_model(db.get(FAQItem,item_id)),before)
            self.assertEqual(db.scalars(select(AuditLog)).all(),[])
        barrier=threading.Barrier(2);outcomes=[]
        def worker(index):
            with Session(self.engine) as db:
                admin=db.get(User,admin_id);barrier.wait(timeout=15)
                try:faq_routes.edit_item(item_id,FAQUpdate(answer=f"Synthetic corrected answer {index}"),db,admin);outcomes.append(200)
                except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
        threads=[threading.Thread(target=worker,args=(index,)) for index in range(2)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads));self.assertEqual(outcomes,[200,200])
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog).order_by(AuditLog.id)).all();self.assertEqual(len(logs),2)
            self.assertEqual(logs[0].old_value,before);self.assertEqual(logs[1].old_value,logs[0].new_value)
            self.assertEqual(logs[1].new_value,snapshot_model(db.get(FAQItem,item_id)))
            self.assertFalse(db.get(FAQItem,item_id).is_published)

    def test_history_pair_metadata_is_distinct_without_loading_or_losing_old_records(self):
        from sqlalchemy import event
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.services.price_update_service import list_price_history_pairs
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic history admin",email="pg-pairs@example.com",password_hash="unused",role="admin",referral_code="PGPAIRS")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market")
            db.add_all([admin,commodity,market]);db.flush()
            for age in range(101):
                db.add(PriceUpdate(commodity_id=commodity.id,market_id=market.id,price_low=210000,price_high=220000,
                    unit="1 bag",bag_size=None,movement="unknown",confidence_level="Low confidence",status="approved",
                    is_outdated=True,update_date_time=datetime.now(timezone.utc)-timedelta(hours=age),created_by=admin.id,source_1="PRIVATE-PAIR-SOURCE"))
            db.commit()
        with Session(self.engine) as db:
            table=PriceUpdate.__table__;before=db.execute(select(table)).all();loaded=[];statements=[]
            event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(type(instance).__name__))
            def capture(connection,cursor,statement,parameters,context,many):statements.append(statement)
            event.listen(self.engine,"before_cursor_execute",capture)
            pairs=list_price_history_pairs(db)
            event.remove(self.engine,"before_cursor_execute",capture)
            self.assertEqual(pairs,[{"commodity":{"name":"Egusi"},"market":{"name":"Kwali Market"}}])
            self.assertEqual(loaded,[]);self.assertEqual(len(statements),1);self.assertIn("DISTINCT",statements[0])
            self.assertEqual(db.execute(select(table)).all(),before);self.assertEqual(len(before),101)

    def test_utc_price_entry_round_trip_and_correction_preserve_other_history(self):
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.schemas.price_update_schema import PriceUpdateCreate, PriceUpdateUpdate
        from app.routes.price_update_routes import add_price_update, edit_price_update
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic time admin",email="pg-time@example.com",password_hash="unused",role="admin",referral_code="PGTIME")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market")
            db.add_all([admin,commodity,market]);db.flush()
            payload=dict(commodity_id=commodity.id,market_id=market.id,price_low=210000,price_high=220000,average_price=215000,
                unit="1 bag",bag_size="Unknown",confidence_level="Low confidence",movement="unknown",suggested_action="Watch")
            original=PriceUpdate(**payload,update_date_time=datetime(2026,10,15,10,tzinfo=timezone.utc),status="approved",created_by=admin.id)
            db.add(original);db.commit();original_id=original.id
            original_values=db.execute(select(PriceUpdate.__table__).where(PriceUpdate.id==original_id)).one()
            item=add_price_update(PriceUpdateCreate(**payload,update_date_time="2026-10-16T14:30:00.000Z"),db,admin)
            item_id=item.id;db.expire_all()
            self.assertEqual(db.get(PriceUpdate,item_id).update_date_time,datetime(2026,10,16,14,30,tzinfo=timezone.utc))
            edit_price_update(item_id,PriceUpdateUpdate(update_date_time="2026-10-16T15:45:00.000Z"),db,admin)
            db.expire_all();item=db.get(PriceUpdate,item_id)
            self.assertEqual(item.update_date_time,datetime(2026,10,16,15,45,tzinfo=timezone.utc))
            self.assertEqual(item.unit,"1 bag");self.assertEqual(item.bag_size,"Unknown");self.assertEqual(item.status,"pending")
            self.assertEqual(db.execute(select(PriceUpdate.__table__).where(PriceUpdate.id==original_id)).one(),original_values)
            self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.record_id==item_id,AuditLog.table_name=="price_updates")).all()),2)

    def test_admin_access_and_revocation_rollback_with_second_audit_failure(self):
        from app.routes import user_routes, subscription_routes
        from app.schemas.subscription_schema import SubscriptionStatusUpdate
        from app.services.audit_service import create_audit_log
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic audit admin",email="pg-access-admin@example.com",password_hash="unused",role="admin",referral_code="PGACCADMIN")
            user=User(full_name="Synthetic audit customer",email="pg-access@example.com",password_hash="preserved",role="free_user",referral_code="PGACCESS")
            user.subscription=build_trial_subscription(user=user)
            db.add_all([admin,user]);db.commit();admin_id,user_id=admin.id,user.id
        def snapshot(db):
            return {table:db.execute(select(table)).all() for table in (User.__table__,Subscription.__table__,AuditLog.__table__)}
        for route in (user_routes,subscription_routes):
            with Session(self.engine) as db:
                before=snapshot(db);admin=db.get(User,admin_id);calls=0
                def audit(*args,**kwargs):
                    nonlocal calls
                    calls+=1
                    if calls==2:raise RuntimeError("Synthetic second audit failure")
                    return create_audit_log(*args,**kwargs)
                with patch.object(route,"create_audit_log",side_effect=audit),self.assertRaisesRegex(RuntimeError,"Synthetic second audit failure"):
                    if route is user_routes:
                        route.edit_user(user_id,AdminUserUpdate(role="paid_user",is_active=False),db,admin)
                    else:
                        route.set_subscription_status(user_id,SubscriptionStatusUpdate(status="active"),db,admin)
                self.assertEqual(calls,2);self.assertEqual(snapshot(db),before)

    def test_concurrent_admin_status_changes_preserve_continuous_audit_snapshots(self):
        from app.routes.subscription_routes import set_subscription_status
        from app.schemas.subscription_schema import SubscriptionStatusUpdate
        from app.services.audit_service import snapshot_model
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic status admin",email="pg-status-admin@example.com",password_hash="unused",role="admin",referral_code="PGSTATADMIN")
            user=User(full_name="Synthetic status customer",email="pg-status@example.com",password_hash="preserved",role="free_user",referral_code="PGSTATUS")
            user.subscription=build_trial_subscription(user=user)
            db.add_all([admin,user]);db.commit();admin_id,user_id=admin.id,user.id;before=snapshot_model(user.subscription)
        barrier=threading.Barrier(2);outcomes=[]
        def worker(status):
            with Session(self.engine) as db:
                admin=db.get(User,admin_id);barrier.wait(timeout=15)
                try:set_subscription_status(user_id,SubscriptionStatusUpdate(status=status),db,admin);outcomes.append(200)
                except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
        threads=[threading.Thread(target=worker,args=(status,)) for status in ("active","free")]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads));self.assertEqual(outcomes,[200,200])
        with Session(self.engine) as db:
            logs=db.scalars(select(AuditLog).where(AuditLog.action=="subscription.status_update").order_by(AuditLog.id)).all()
            self.assertEqual(len(logs),2);self.assertEqual(logs[0].old_value,before)
            self.assertEqual(logs[1].old_value,logs[0].new_value)
            user=db.get(User,user_id)
            self.assertEqual(logs[1].new_value,snapshot_model(user.subscription))
            self.assertEqual(user.role,"paid_user" if user.subscription.status=="active" else "free_user")
            self.assertEqual(user.password_hash,"preserved");self.assertEqual(user.auth_version,0)

    def test_admin_summary_is_one_read_snapshot_without_loading_customer_rows(self):
        from sqlalchemy import event
        from app.models.commodity import Commodity
        from app.models.feedback import Feedback
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.services.admin_summary_service import get_admin_summary
        Base.metadata.create_all(self.engine)
        now = datetime.now(timezone.utc)
        with Session(self.engine) as db:
            admin = User(full_name="Synthetic summary admin", email="pgsummaryadmin@example.com", password_hash="unused", role="admin", referral_code="PGSUMADMIN")
            trial = User(full_name="Synthetic summary trial", email="pgsummarytrial@example.com", password_hash="unused", role="free_user", referral_code="PGSUMTRIAL")
            trial.subscription = build_trial_subscription(user=trial, now=now)
            commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
            db.add_all([admin, trial, commodity, market]); db.flush()
            trial.referred_by_id = admin.id
            for age in range(100, -1, -1):
                db.add(PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=210000, price_high=220000,
                    unit="1 bag", bag_size=None, movement="unknown", confidence_level="Low confidence", status="approved",
                    is_outdated=age==100, update_date_time=now-timedelta(hours=age), created_by=admin.id, source_1="PRIVATE-SUMMARY-SOURCE"))
            for rating,public in ((4,False),(5,True)):
                db.add(Feedback(user_id=trial.id, rating=rating, is_public_testimonial=public, comment="Synthetic summary", screenshot_data="data:image/png;base64,WA=="))
            for index,(status,plan,amount) in enumerate((("success","monthly",2500),("success","seasonal",6000),("pending","monthly",2500))):
                db.add(Payment(user_id=trial.id, reference="py_pg_summary_"+str(index), status=status, plan=plan, amount=amount, currency="NGN"))
            db.commit()
        with Session(self.engine) as db:
            before = {table:db.execute(select(table)).all() for table in (User.__table__,Subscription.__table__,PriceUpdate.__table__,Feedback.__table__,Payment.__table__)}
            loaded=[]; statements=[]
            event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(type(instance).__name__))
            def capture(connection,cursor,statement,parameters,context,many): statements.append(statement)
            event.listen(self.engine,"before_cursor_execute",capture)
            summary=get_admin_summary(db)
            event.remove(self.engine,"before_cursor_execute",capture)
            self.assertEqual(loaded,[]); self.assertEqual(len(statements),1)
            self.assertEqual(summary.model_dump(),dict(users=2,commodities=1,markets=1,latest=1,outdated=1,trial=1,active=2,
                feedback=2,average=4.5,newUsersWeek=2,referralsUsed=1,testimonialsLive=1,successfulPayments=2,revenue=Decimal("8500")))
            for table,rows in before.items(): self.assertEqual(db.execute(select(table)).all(),rows)

    def google_signup_race(self, *, same_subject):
        from app.services.auth_service import authenticate_or_create_google_user
        Base.metadata.create_all(self.engine)
        barrier = threading.Barrier(2); outcomes = []; subjects = []
        def verifier(token, request, audience):
            barrier.wait(timeout=15)
            return {"sub":"synthetic-pg-google-"+("same" if same_subject else token), "email":"pg-google-new@example.com", "email_verified":True}
        def worker(index):
            with Session(self.engine, expire_on_commit=False) as db:
                try:
                    user = authenticate_or_create_google_user(db, "synthetic-google-token-"+str(index))
                    outcomes.append(200); subjects.append(user.id)
                except HTTPException as error:
                    db.rollback(); outcomes.append(error.status_code)
                except BaseException as error:
                    db.rollback(); outcomes.append(type(error).__name__)
        with patch("app.services.auth_service.google_id_token.verify_oauth2_token", side_effect=verifier):
            threads = [threading.Thread(target=worker, args=(index,)) for index in range(2)]
            for thread in threads: thread.start()
            for thread in threads: thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes, [200, 200] if same_subject else [200, 409])
        with Session(self.engine) as db:
            rows = db.scalars(select(User)).all(); self.assertEqual(len(rows), 1)
            self.assertTrue(all(user_id == rows[0].id for user_id in subjects))
            self.assertEqual(rows[0].subscription.trial_ends_at-rows[0].subscription.trial_started_at, timedelta(days=14))
            self.assertEqual(len(db.scalars(select(Subscription)).all()), 1)

    def test_concurrent_same_google_subject_has_one_account_and_trial(self):
        self.google_signup_race(same_subject=True)

    def test_concurrent_different_google_subjects_cannot_claim_same_email(self):
        self.google_signup_race(same_subject=False)

    def test_google_email_collision_preserves_existing_paid_account_and_binding(self):
        from app.services.auth_service import authenticate_or_create_google_user
        Base.metadata.create_all(self.engine)
        with Session(self.engine, expire_on_commit=False) as db:
            user = User(full_name="Synthetic Google owner", email="pg-google-existing@example.com", password_hash="original-unused-hash",
                        role="reporter", referral_code="PGGOOGLE", google_id="existing-owned-google-subject", auth_version=4)
            user.subscription = Subscription(status="active", plan_name="paid_monthly", end_date=datetime.now(timezone.utc).date()+timedelta(days=12))
            db.add(user); db.commit()
            before = (user.id, user.password_hash, user.google_id, user.role, user.auth_version, user.subscription.end_date)
            claims = {"sub":"unmatched-google-subject", "email":user.email, "email_verified":True}
            with patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value=claims):
                with self.assertRaises(HTTPException) as denied:
                    authenticate_or_create_google_user(db, "synthetic-google-token")
                self.assertEqual(denied.exception.status_code, 409)
            db.rollback(); db.expire_all(); restored = db.get(User, before[0])
            self.assertEqual((restored.id, restored.password_hash, restored.google_id, restored.role, restored.auth_version, restored.subscription.end_date), before)
            claims.update(sub=restored.google_id, email="changed-google-email@example.com")
            with patch("app.services.auth_service.google_id_token.verify_oauth2_token", return_value=claims):
                linked = authenticate_or_create_google_user(db, "synthetic-google-token")
            self.assertEqual(linked.id, before[0]); self.assertEqual(linked.email, "pg-google-existing@example.com")

    def test_original_feedback_screenshot_and_private_fields_are_preserved(self):
        from pydantic import ValidationError
        from app.models.feedback import Feedback
        from app.schemas.feedback_schema import FeedbackCreate, MAX_SCREENSHOT_BYTES
        from app.services.feedback_service import create_feedback, get_feedback, list_public_testimonials
        Base.metadata.create_all(self.engine)
        image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        with Session(self.engine) as db:
            user = User(full_name="Synthetic feedback", email="pgfeedback@example.com", password_hash="unused", role="free_user", referral_code="PGFEEDBACK")
            db.add(user); db.commit()
            item = create_feedback(db, user, FeedbackCreate(rating=5, screenshot_data=image, complaint_or_suggestion="Synthetic screenshot evidence", continue_using_feedback=True))
            saved_id = item.id
            self.assertEqual(list_public_testimonials(db), [])
            with self.assertRaises(ValidationError):
                FeedbackCreate(rating=5, screenshot_data="data:image/png;base64," + "A" * (4*((MAX_SCREENSHOT_BYTES+2)//3)+4))
        with Session(self.engine) as db:
            item = get_feedback(db, saved_id)
            self.assertEqual(item.screenshot_data, image)
            self.assertEqual(item.complaint_or_suggestion, "Synthetic screenshot evidence")
            self.assertTrue(item.continue_using_feedback)
            self.assertEqual(len(db.scalars(select(Feedback)).all()), 1)

    def test_concurrent_price_edits_preserve_ordered_atomic_audit(self):
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.routes.price_update_routes import edit_price_update
        from app.schemas.price_update_schema import PriceUpdateUpdate
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic editor", email="pgeditor@example.com", password_hash="unused", role="admin", referral_code="PGEDITOR")
            commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
            db.add_all([user, commodity, market]); db.flush(); user_id = user.id
            price = PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=210000,
                price_high=220000, average_price=215000, unit="1 bag", bag_size=None,
                confidence_level="Low confidence", movement="unknown", status="pending",
                update_date_time=datetime.now(timezone.utc), created_by=user.id,
                source_1="PG-PRIVATE-FAKE-SOURCE")
            db.add(price); db.flush(); price_id = price.id; db.commit()
        barrier = threading.Barrier(2); outcomes = []
        def worker(low):
            with Session(self.engine, expire_on_commit=False) as db:
                user = db.get(User, user_id); barrier.wait(timeout=15)
                try:
                    edit_price_update(price_id, PriceUpdateUpdate(price_low=low), db, user)
                    outcomes.append(200)
                except BaseException as error:
                    db.rollback(); outcomes.append(type(error).__name__)
        threads = [threading.Thread(target=worker, args=(low,)) for low in (209000, 208000)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads)); self.assertEqual(outcomes, [200, 200])
        with Session(self.engine) as db:
            logs = db.scalars(select(AuditLog).order_by(AuditLog.id)).all()
            self.assertEqual(len(logs), 2)
            self.assertEqual(float(logs[0].old_value["price_low"]), 210000)
            self.assertEqual(Decimal(logs[0].new_value["price_low"]), Decimal(logs[1].old_value["price_low"]))
            self.assertEqual(float(logs[1].new_value["price_low"]), db.get(PriceUpdate, price_id).price_low)
            self.assertNotIn("PG-PRIVATE-FAKE-SOURCE", str([(log.old_value, log.new_value) for log in logs]))

    def test_current_price_ranking_bounds_hydration_without_losing_history(self):
        from sqlalchemy import event, func
        from app.models.commodity import Commodity
        from app.models.market import Market
        from app.models.price_update import PriceUpdate
        from app.services.price_update_service import list_latest_approved_price_updates, list_price_history
        Base.metadata.create_all(self.engine)
        now = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic query", email="pgquery@example.com", password_hash="unused", role="admin", referral_code="PGQUERY")
            commodity = Commodity(name="Egusi", is_active=True)
            market = Market(name="Kwali Market", is_active=True)
            db.add_all([user, commodity, market]); db.flush()
            for age in range(150, -1, -1):
                db.add(PriceUpdate(commodity_id=commodity.id, market_id=market.id,
                    price_low=210000, price_high=220000, unit="1 bag", bag_size=None,
                    confidence_level="Low confidence", movement="up" if age == 0 else "down",
                    update_date_time=now-timedelta(hours=age), status="approved", created_by=user.id))
            db.commit()
        with Session(self.engine) as db:
            loaded = []
            @event.listens_for(db, "loaded_as_persistent")
            def count_load(session, instance):
                if isinstance(instance, PriceUpdate): loaded.append(instance.id)
            records = list_latest_approved_price_updates(db)
            self.assertEqual(len(records), 1); self.assertEqual(loaded, [records[0].id])
            self.assertEqual(records[0].unit, "1 bag"); self.assertIsNone(records[0].bag_size)
            self.assertEqual(list_latest_approved_price_updates(db, movement="down"), [])
            # Native PostgreSQL returns timestamptz in its session timezone.
            self.assertEqual(list_latest_approved_price_updates(db, selected_date=now.date()-timedelta(days=1))[0].update_date_time.astimezone(timezone.utc).hour, 23)
            records[0].is_outdated = True; db.commit()
            self.assertEqual(list_latest_approved_price_updates(db), [])
            self.assertEqual(len(list_price_history(db)), 151)
            self.assertEqual(db.scalar(select(func.count()).select_from(PriceUpdate)), 151)

    def setUp(self):
        global CURRENT_SCHEMA
        CURRENT_SCHEMA = None
        self.admin = pinned_engine(URL)
        self.schema = "pyrev_" + uuid.uuid4().hex
        with self.admin.begin() as connection:
            connection.execute(text('CREATE SCHEMA "'+self.schema+'"'))
        CURRENT_SCHEMA = self.schema
        self.engine = pinned_engine(URL)

    def tearDown(self):
        global CURRENT_SCHEMA
        self.engine.dispose()
        # Preserve synthetic schemas/evidence; no DROP or destructive cleanup.
        self.admin.dispose()
        CURRENT_SCHEMA = None

    def config(self):
        config = Config()
        config.set_main_option("script_location", str(ROOT / "backend/migrations"))
        return config

    def test_fresh_and_populated_migration_preserves_original_records(self):
        command.upgrade(self.config(), "0021_feedback_screenshot")
        with self.engine.begin() as connection:
            user_id = connection.execute(text("INSERT INTO users(full_name,email,password_hash,role,is_active,referral_code) VALUES ('Synthetic preservation','preservation@example.com','unchanged-hash','paid_user',true,'PGPRESERVE') RETURNING id")).scalar_one()
            connection.execute(text("INSERT INTO subscriptions(user_id,plan_name,status,start_date,end_date,payment_reference) VALUES (:id,'paid_monthly','active','2026-10-16','2026-11-15','synthetic-preserved')"), {"id":user_id})
            connection.execute(text("INSERT INTO payments(user_id,reference,plan,amount,currency,status) VALUES (:id,'synthetic-preserved','monthly',2500,'NGN','success')"), {"id":user_id})
            connection.execute(text("INSERT INTO price_updates(commodity_id,market_id,price_low,price_high,average_price,unit,movement,is_outdated,confidence_level,source_1,update_date_time,status,created_by) SELECT c.id,m.id,210000,220000,215000,'1 bag','unknown',false,'Low confidence','LOCAL-PRIVATE-SOURCE','2026-10-15T12:00:00Z','approved',:id FROM commodities c CROSS JOIN markets m WHERE c.name='Egusi' AND m.name='Kwali Market'"), {"id":user_id})
            before = {table: connection.execute(text('SELECT to_jsonb(t) FROM '+table+' t ORDER BY id')).scalars().all() for table in ("users","subscriptions","payments","commodities","markets","price_updates")}
        command.upgrade(self.config(), "head")
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one(), "0022_login_revocation")
            self.assertEqual(connection.execute(text("SELECT auth_version FROM users WHERE id=:id"),{"id":user_id}).scalar_one(),0)
            for table, rows in before.items():
                after = connection.execute(text('SELECT to_jsonb(t) FROM '+table+' t ORDER BY id')).scalars().all()
                if table == "users":
                    for row in after: row.pop("auth_version")
                self.assertEqual(after, rows, table)
            self.assertEqual(connection.execute(text("SELECT count(*) FROM revoked_access_tokens")).scalar_one(),0)
        with self.assertRaises(RuntimeError):
            command.downgrade(self.config(), "0021_feedback_screenshot")
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one(),"0022_login_revocation")

    def seed_security(self):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic race",email="race@example.com",password_hash=hash_password("OldPassword1"),role="free_user",is_active=True,referral_code="PGRACE")
            db.add(user);db.flush()
            raw = "synthetic-reset-"+"x"*40
            db.add(PasswordResetToken(user_id=user.id,token_hash=hashlib.sha256(raw.encode()).hexdigest(),expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)))
            db.commit();return user.id,raw

    def test_concurrent_reset_has_one_winner_and_revokes_previous_version(self):
        user_id, raw = self.seed_security()
        barrier = threading.Barrier(2)
        original_hash = password_reset_service.hash_password
        outcomes = []
        def synchronized_hash(password):
            barrier.wait(timeout=15)
            return original_hash(password)
        def worker(password):
            with Session(self.engine) as db:
                try:
                    password_reset_service.reset_password(db,token=raw,new_password=password)
                    outcomes.append(200)
                except HTTPException as error:
                    db.rollback();outcomes.append(error.status_code)
                except BaseException as error:
                    db.rollback();outcomes.append(type(error).__name__)
        with patch.object(password_reset_service,"hash_password",synchronized_hash):
            threads=[threading.Thread(target=worker,args=(password,)) for password in ("NewPassword1","OtherPassword1")]
            for thread in threads:thread.start()
            for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes,[200,400])
        with Session(self.engine) as db:
            self.assertEqual(db.get(User,user_id).auth_version,1)
            self.assertIsNotNone(db.scalar(select(PasswordResetToken)).used_at)

    def test_concurrent_logout_is_idempotent_and_stores_only_hash(self):
        user_id,_ = self.seed_security()
        token=create_access_token(user_id=user_id)
        barrier=threading.Barrier(2)
        original_get=Session.get
        outcomes=[]
        def synchronized_get(db,entity,*args,**kwargs):
            value=original_get(db,entity,*args,**kwargs)
            if entity is RevokedAccessToken and value is None:barrier.wait(timeout=15)
            return value
        def worker():
            with Session(self.engine) as db:
                try:
                    user=db.get(User,user_id)
                    revoke_token(db,user,token,expires_at=datetime.now(timezone.utc)+timedelta(days=90))
                    outcomes.append("ok")
                except BaseException as error:outcomes.append(type(error).__name__)
        with patch.object(Session,"get",synchronized_get):
            threads=[threading.Thread(target=worker) for _ in range(2)]
            for thread in threads:thread.start()
            for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(outcomes,["ok","ok"])
        with Session(self.engine) as db:
            rows=db.scalars(select(RevokedAccessToken)).all()
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0].token_hash,hashlib.sha256(token.encode()).hexdigest())
            self.assertTrue(is_revoked(db,token))

    def test_distinct_reset_links_for_one_user_do_not_deadlock(self):
        user_id, first = self.seed_security()
        second = "synthetic-second-reset-"+"y"*40
        with Session(self.engine) as db:
            db.add(PasswordResetToken(user_id=user_id,token_hash=hashlib.sha256(second.encode()).hexdigest(),expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)))
            db.commit()
        barrier=threading.Barrier(2)
        original_hash=password_reset_service.hash_password
        outcomes=[]
        def synchronized_hash(password):
            barrier.wait(timeout=15)
            return original_hash(password)
        def worker(token,password):
            with Session(self.engine) as db:
                try:
                    password_reset_service.reset_password(db,token=token,new_password=password)
                    outcomes.append(200)
                except HTTPException as error:
                    db.rollback();outcomes.append(error.status_code)
                except BaseException as error:
                    db.rollback();outcomes.append(type(error).__name__)
        with patch.object(password_reset_service,"hash_password",synchronized_hash):
            threads=[threading.Thread(target=worker,args=pair) for pair in ((first,"NewPassword1"),(second,"OtherPassword1"))]
            for thread in threads:thread.start()
            for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes,[200,400])
        with Session(self.engine) as db:
            self.assertEqual(db.get(User,user_id).auth_version,1)
            self.assertTrue(all(token.used_at is not None for token in db.scalars(select(PasswordResetToken))))

    def admin_race(self, payload):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admins=[]
            for index in range(2):
                user=User(full_name="Synthetic admin",email=f"admin{index}@example.com",password_hash="not-used",role="admin",is_active=True,referral_code=f"PGADMIN{index}")
                # Past trials catch accidental commits by expiry helpers too.
                user.subscription=build_trial_subscription(user=user,now=datetime(2000,1,1,tzinfo=timezone.utc))
                db.add(user);admins.append(user)
            db.commit();ids=[user.id for user in admins]
        barrier=threading.Barrier(2)
        outcomes=[]
        def worker(user_id):
            with Session(self.engine) as db:
                user=db.get(User,user_id)
                barrier.wait(timeout=15)
                try:
                    update_user(db,user,AdminUserUpdate(**payload));outcomes.append(200)
                except HTTPException as error:
                    db.rollback();outcomes.append(error.status_code)
                except BaseException as error:
                    db.rollback();outcomes.append(type(error).__name__)
        threads=[threading.Thread(target=worker,args=(user_id,)) for user_id in ids]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes,[200,409])
        with Session(self.engine) as db:
            remaining=db.scalars(select(User).where(User.role=="admin",User.is_active.is_(True))).all()
            self.assertEqual(len(remaining),1)

    def test_concurrent_last_admin_deactivation_is_prevented(self):
        self.admin_race({"is_active":False})

    def test_concurrent_last_admin_demotion_keeps_one_admin(self):
        self.admin_race({"role":"free_user"})

    def payment_race(self, *, duplicate_transaction, distinct_purchases=False, verification=False):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user=User(full_name="Synthetic payer",email="pgpayment@example.com",password_hash="not-used",role="free_user",is_active=True,referral_code="PGPAY")
            user.subscription=build_trial_subscription(user=user,now=datetime(2000,1,1,tzinfo=timezone.utc))
            db.add(user);db.flush()
            references=["py_concurrent_one","py_concurrent_two"] if duplicate_transaction or distinct_purchases else ["py_concurrent_one"]
            for reference in references:
                db.add(Payment(user_id=user.id,reference=reference,plan="monthly",amount=2500,currency="NGN",status="pending"))
            db.commit();user_id=user.id
        barrier=threading.Barrier(2)
        outcomes=[]
        def delay_payment_write(connection,cursor,statement,parameters,context,executemany):
            # Widen the old read/write race without waiting inside a protected
            # region for another worker that is correctly waiting on its lock.
            if statement.lstrip().upper().startswith("UPDATE PAYMENTS"):
                time.sleep(0.1)
        sqlalchemy.event.listen(self.engine,"before_cursor_execute",delay_payment_write)
        def worker(reference, verify=False):
            transaction_id = 808081 if distinct_purchases and reference == "py_concurrent_two" else 808080
            payload={"event":"charge.success","data":{"reference":reference,"id":transaction_id,"amount":250000,"currency":"NGN","status":"success"}}
            with Session(self.engine) as db:
                barrier.wait(timeout=15)
                try:
                    if verify:
                        payment_service.verify_recorded_payment(db,db.get(User,user_id),reference)
                    else:
                        payment_service.handle_webhook_event(db,payload)
                    outcomes.append(200)
                except HTTPException as error:
                    db.rollback();outcomes.append(error.status_code)
                except BaseException as error:
                    db.rollback();outcomes.append(type(error).__name__)
        import json
        import requests
        from types import SimpleNamespace
        def provider(session, method, url, **kwargs):
            if method.upper() != "GET" or url != "https://api.paystack.co/transaction/verify/py_concurrent_one":
                raise RuntimeError("Only a mocked payment verification is allowed")
            response=requests.Response();response.status_code=200
            response._content=json.dumps({"status":True,"data":{"reference":"py_concurrent_one","id":808080,"amount":250000,"currency":"NGN","status":"success"}}).encode()
            return response
        settings=SimpleNamespace(paystack_secret_key="sk_test_synthetic_pg_only",frontend_url="http://127.0.0.1:55446")
        with patch.object(payment_service,"notify_admins",return_value=None),patch.object(payment_service,"get_settings",return_value=settings),patch("requests.Session.request",autospec=True,side_effect=provider):
            worker_references=references if duplicate_transaction or distinct_purchases else references*2
            threads=[threading.Thread(target=worker,args=(reference,verification and index==0)) for index,reference in enumerate(worker_references)]
            for thread in threads:thread.start()
            for thread in threads:thread.join(25)
        sqlalchemy.event.remove(self.engine,"before_cursor_execute",delay_payment_write)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes,[200,409] if duplicate_transaction else [200,200])
        with Session(self.engine) as db:
            payments=db.scalars(select(Payment)).all()
            expected_count = 2 if distinct_purchases else 1
            self.assertEqual(sum(payment.status=="success" for payment in payments),expected_count)
            self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action=="payment.success")).all()),expected_count)
            subscription=db.get(User,user_id).subscription
            self.assertEqual(subscription.status,"active")
            self.assertIn(subscription.payment_reference,references)
            self.assertEqual(subscription.end_date, datetime.now(timezone.utc).date()+timedelta(days=30*expected_count))

    def test_concurrent_distinct_purchases_preserve_both_durations(self):
        self.payment_race(duplicate_transaction=False, distinct_purchases=True)

    def test_concurrent_payment_replay_applies_access_and_audit_once(self):
        self.payment_race(duplicate_transaction=False)

    def test_one_provider_transaction_cannot_credit_concurrent_purchases(self):
        self.payment_race(duplicate_transaction=True)

    def test_provider_verification_and_webhook_share_one_credit(self):
        self.payment_race(duplicate_transaction=False,verification=True)

    def referral_race(self, *, same_email):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            referrer=User(full_name="Synthetic referral parent",email="pgreferrer@example.com",password_hash="not-used",role="free_user",is_active=True,referral_code="PGREF")
            referrer.subscription=build_trial_subscription(user=referrer)
            db.add(referrer);db.commit();referrer_id=referrer.id;original_end=referrer.subscription.trial_ends_at
        barrier=threading.Barrier(2);outcomes=[]
        def worker(index):
            payload=RegisterRequest(full_name="Synthetic referral child",email=f"pgchild{0 if same_email else index}@example.com",password="PriceYardDemo8!",referral_code="PGREF")
            with Session(self.engine) as db:
                barrier.wait(timeout=15)
                try:register_user(db,payload);outcomes.append(201)
                except HTTPException as error:db.rollback();outcomes.append(error.status_code)
                except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
        threads=[threading.Thread(target=worker,args=(index,)) for index in range(2)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes,[201,409] if same_email else [201,201])
        expected=1 if same_email else 2
        with Session(self.engine) as db:
            self.assertEqual(db.get(User,referrer_id).subscription.trial_ends_at,original_end+timedelta(days=7*expected))
            children=db.scalars(select(User).where(User.referred_by_id==referrer_id)).all();self.assertEqual(len(children),expected)
            for child in children:self.assertEqual(child.subscription.trial_ends_at-child.subscription.trial_started_at,timedelta(days=14))
            self.assertEqual(len(db.scalars(select(AuditLog).where(AuditLog.action=="referral.reward_granted")).all()),expected)

    def test_distinct_simultaneous_registrations_keep_both_referral_rewards(self):
        self.referral_race(same_email=False)

    def test_duplicate_simultaneous_registration_only_rewards_once(self):
        self.referral_race(same_email=True)

    def test_concurrent_manual_grant_purchase_holds_then_recovers_once(self):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user=User(full_name="Synthetic indefinite payer",email="pghold@example.com",password_hash="not-used",role="paid_user",is_active=True,referral_code="PGHOLD")
            user.subscription=Subscription(plan_name="paid",status="active",end_date=None)
            db.add(user);db.flush();user_id=user.id
            db.add(Payment(user_id=user.id,reference="py_pg_review",plan="monthly",amount=2500,currency="NGN",status="pending"));db.commit()
        payload={"event":"charge.success","data":{"reference":"py_pg_review","id":606060,"amount":250000,"currency":"NGN","status":"success"}}
        def race(expected):
            barrier=threading.Barrier(2);outcomes=[]
            def worker():
                with Session(self.engine) as db:
                    barrier.wait(timeout=15)
                    try:payment_service.handle_webhook_event(db,payload);outcomes.append(200)
                    except HTTPException as error:db.rollback();outcomes.append(error.status_code)
                    except BaseException as error:db.rollback();outcomes.append(type(error).__name__)
            with patch.object(payment_service,"notify_admins",return_value=None):
                threads=[threading.Thread(target=worker) for _ in range(2)]
                for thread in threads:thread.start()
                for thread in threads:thread.join(25)
            self.assertFalse(any(thread.is_alive() for thread in threads));self.assertEqual(outcomes,[expected,expected])
        race(409)
        with Session(self.engine) as db:
            self.assertIsNone(db.get(User,user_id).subscription.end_date)
            payment=db.scalar(select(Payment));self.assertEqual(payment.status,"pending");self.assertEqual(payment.paystack_transaction_id,"606060")
            self.assertEqual([item.action for item in db.scalars(select(AuditLog))],["payment.review_required"])
            update_subscription_status(db,db.get(User,user_id).subscription,"free")
        race(200)
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(Payment)).status,"success")
            self.assertEqual(db.get(User,user_id).subscription.end_date,datetime.now(timezone.utc).date()+timedelta(days=30))
            self.assertCountEqual([item.action for item in db.scalars(select(AuditLog))],["payment.review_required","payment.success"])

    def test_concurrent_push_registration_cannot_overwrite_other_device_keys(self):
        import base64
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            users=[]
            for index in range(2):
                user=User(full_name="Synthetic push race",email=f"pgrace{index}@example.com",password_hash="not-used",role="free_user",is_active=True,referral_code=f"PGPUSH{index}")
                db.add(user);db.flush();users.append(user.id)
            db.commit()
        encode=lambda value:base64.urlsafe_b64encode(value).decode().rstrip("=")
        public=ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
        payloads=[PushSubscriptionCreate(endpoint="https://fcm.googleapis.com/fcm/send/synthetic-race",keys={"p256dh":encode(public),"auth":encode(bytes([index])*16)}) for index in range(2)]
        barrier=threading.Barrier(2);outcomes=[]
        def worker(index):
            with Session(self.engine) as db:
                user=db.get(User,users[index]);barrier.wait(timeout=15)
                try:
                    save_subscription(db,user,payloads[index]);outcomes.append((index,204))
                except HTTPException as error:
                    db.rollback();outcomes.append((index,error.status_code))
                except BaseException as error:
                    db.rollback();outcomes.append((index,type(error).__name__))
        threads=[threading.Thread(target=worker,args=(index,)) for index in range(2)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(25)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertCountEqual([status for _,status in outcomes],[204,409])
        winner=next(index for index,status in outcomes if status==204)
        with Session(self.engine) as db:
            rows=db.scalars(select(PushSubscription)).all();self.assertEqual(len(rows),1)
            self.assertEqual(rows[0].user_id,users[winner]);self.assertEqual(rows[0].auth,payloads[winner].keys.auth)


if __name__ == "__main__":
    # Negative connection checks reject before any native/network call.
    for arguments in (dict(host="127.0.0.1",port=5432,user=marker["user"],dbname=marker["database"]),dict(host="service.example.invalid",port=55447,user=marker["user"],dbname=marker["database"])):
        try:pinned_connect(**arguments)
        except RuntimeError:pass
        else:raise RuntimeError("Connection isolation negative failed")
    started=time.monotonic()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PostgreSQLSecurityTests))
    report={"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"seconds":round(time.monotonic()-started,3),"cluster_identity_verified":True,"production_contacts":0}
    (LAB / "runtime/postgres-security.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
    raise SystemExit(not result.wasSuccessful())
