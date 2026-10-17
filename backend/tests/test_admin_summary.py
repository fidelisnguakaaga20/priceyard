from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.commodity import Commodity
from app.models.feedback import Feedback
from app.models.market import Market
from app.models.payment import Payment
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token


class AdminSummaryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.now = datetime.now(timezone.utc)
        with Session(self.engine) as db:
            users = []
            for index, name in enumerate(("admin", "trial", "expired-trial", "manual", "expired-paid", "disabled")):
                user = User(full_name="Synthetic " + name, email=name+"@example.com", password_hash="unused", referral_code="METRIC"+str(index),
                            role="admin" if index == 0 else "paid_user" if index in (3,4) else "free_user", is_active=index!=5,
                            created_at=self.now-timedelta(days=8 if index==3 else 1))
                if index in (1,2):
                    user.subscription = Subscription(status="trial", plan_name="trial", trial_started_at=self.now-timedelta(days=15 if index==2 else 0), trial_ends_at=self.now+timedelta(days=-1 if index==2 else 14))
                elif index in (3,4):
                    user.subscription = Subscription(status="active", plan_name="paid_monthly", end_date=None if index==3 else self.now.date()-timedelta(days=1))
                elif index == 5:
                    user.subscription = Subscription(status="free", plan_name="free")
                db.add(user); db.flush(); users.append(user)
            users[2].referred_by_id = users[1].id
            self.admin_id = users[0].id; self.trial_id = users[1].id
            self.admin_headers = {"Authorization":"Bearer "+create_access_token(user_id=users[0].id)}
            self.trial_headers = {"Authorization":"Bearer "+create_access_token(user_id=users[1].id)}
            active, inactive = Commodity(name="Egusi"), Commodity(name="Honey Beans", is_active=False)
            market = Market(name="Kwali Market")
            db.add_all([active,inactive,market]); db.flush()
            for commodity, age, status, outdated in ((active,2,"approved",False),(active,0,"approved",False),(active,-1,"pending",False),(inactive,0,"approved",True),(active,-2,"rejected",True)):
                db.add(PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=210000, price_high=220000, unit="1 bag", bag_size=None,
                    movement="unknown", confidence_level="Low confidence", status=status, is_outdated=outdated, update_date_time=self.now-timedelta(days=age), created_by=users[0].id, source_1="PRIVATE-FAKE-SOURCE"))
            for rating, public in ((5,True),(3,False)):
                db.add(Feedback(user_id=users[1].id, rating=rating, is_public_testimonial=public, comment="Synthetic feedback", screenshot_data="data:image/png;base64,WA=="))
            for index, (status, plan, amount) in enumerate((("success","monthly",2500),("success","seasonal",6000),("pending","monthly",2500),("failed","seasonal",6000))):
                db.add(Payment(user_id=users[1].id, reference="py_synthetic_metric_"+str(index), status=status, plan=plan, amount=amount, currency="NGN"))
            db.commit()
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db: yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close(); app.dependency_overrides.clear(); self.engine.dispose()

    def test_admin_endpoint_keeps_all_fourteen_metric_definitions(self):
        response = self.client.get("/admin/summary", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        actual = response.json(); actual["revenue"] = Decimal(actual["revenue"])
        self.assertEqual(actual, {"users":6,"commodities":2,"markets":1,"latest":1,"outdated":2,"trial":1,"active":5,"feedback":2,"average":4.0,
                                  "newUsersWeek":5,"referralsUsed":1,"testimonialsLive":1,"successfulPayments":2,"revenue":Decimal("8500")})
        self.assertNotIn("PRIVATE-FAKE-SOURCE", response.text)
        self.assertNotIn("screenshot", response.text)
        self.assertNotIn("password", response.text)

    def test_guest_and_non_admin_cannot_read_summary(self):
        self.assertEqual(self.client.get("/admin/summary").status_code,401)
        self.assertEqual(self.client.get("/admin/summary",headers=self.trial_headers).status_code,403)

    def test_aggregation_does_not_hydrate_or_modify_original_records(self):
        from app.services.admin_summary_service import get_admin_summary
        with Session(self.engine) as db:
            before = {table:db.execute(select(table)).all() for table in (User.__table__,Subscription.__table__,PriceUpdate.__table__,Feedback.__table__,Payment.__table__)}
            loaded=[]
            event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(type(instance).__name__))
            statements=[]
            def capture(connection,cursor,statement,parameters,context,many): statements.append(statement)
            event.listen(self.engine,"before_cursor_execute",capture)
            result=get_admin_summary(db)
            event.remove(self.engine,"before_cursor_execute",capture)
            self.assertEqual(result.users,6); self.assertEqual(loaded,[])
            self.assertEqual(len(statements),1,"Dashboard totals must use one read snapshot")
            for table,rows in before.items(): self.assertEqual(db.execute(select(table)).all(),rows)

    def test_empty_database_has_zero_counts_and_no_average(self):
        from app.services.admin_summary_service import get_admin_summary
        empty=create_engine("sqlite+pysqlite:///:memory:"); Base.metadata.create_all(empty)
        try:
            with Session(empty) as db:
                result=get_admin_summary(db).model_dump()
                self.assertIsNone(result.pop("average")); self.assertTrue(all(value==0 for value in result.values()))
        finally: empty.dispose()

    def test_seven_day_boundary_is_inclusive_and_not_browser_clock_dependent(self):
        from app.services.admin_summary_service import get_admin_summary
        with Session(self.engine) as db:
            for index,age in enumerate((timedelta(days=7),timedelta(days=7,microseconds=1))):
                db.add(User(full_name="Synthetic boundary",email=f"boundary{index}@example.com",password_hash="unused",role="free_user",referral_code=f"BOUNDARY{index}",created_at=self.now-age))
            db.commit()
            result=get_admin_summary(db,now=self.now)
            self.assertEqual(result.users,8); self.assertEqual(result.newUsersWeek,6)
