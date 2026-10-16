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
from app.security import create_access_token
from app.services import password_reset_service
from app.services import payment_service
from app.services.login_revocation_service import is_revoked, revoke_token
from app.services.subscription_service import build_trial_subscription
from app.services.user_service import update_user
from app.schemas.user_schema import AdminUserUpdate
from app.utils.password import hash_password


class PostgreSQLSecurityTests(unittest.TestCase):
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

    def payment_race(self, *, duplicate_transaction, distinct_purchases=False):
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
        def worker(reference):
            transaction_id = 808081 if distinct_purchases and reference == "py_concurrent_two" else 808080
            payload={"event":"charge.success","data":{"reference":reference,"id":transaction_id,"amount":250000,"currency":"NGN","status":"success"}}
            with Session(self.engine) as db:
                barrier.wait(timeout=15)
                try:
                    payment_service.handle_webhook_event(db,payload);outcomes.append(200)
                except HTTPException as error:
                    db.rollback();outcomes.append(error.status_code)
                except BaseException as error:
                    db.rollback();outcomes.append(type(error).__name__)
        with patch.object(payment_service,"notify_admins",return_value=None):
            worker_references=references if duplicate_transaction or distinct_purchases else references*2
            threads=[threading.Thread(target=worker,args=(reference,)) for reference in worker_references]
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
