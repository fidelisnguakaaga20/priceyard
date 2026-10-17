from datetime import datetime, timedelta, timezone
import unittest

from pydantic import ValidationError
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_flag_schema import PriceFlagCreate
from app.services.price_flag_service import list_flagged_price_updates


class FlagReviewQueryTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        now=datetime.now(timezone.utc)
        with Session(self.engine) as db:
            users=[User(full_name="Synthetic flag reviewer",email=f"flag-query-{i}@example.com",password_hash="unused",role="admin" if i==0 else "free_user",referral_code=f"FLAGQ{i}") for i in range(3)]
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market");db.add_all([*users,commodity,market]);db.flush();self.ids=[]
            for age,state in ((2,"approved"),(1,"rejected"),(0,"pending")):
                price=PriceUpdate(commodity_id=commodity.id,market_id=market.id,unit="1 bag",bag_size=None,
                    price_low=210000,price_high=220000,status=state,movement="unknown",confidence_level="Low confidence",
                    update_date_time=now-timedelta(days=age),created_by=users[0].id,source_1="PRIVATE-FLAG-QUERY-SOURCE")
                db.add(price);db.flush();self.ids.append(price.id)
                for index,user in enumerate(users):db.add(PriceFlag(price_update_id=price.id,user_id=user.id,reason="Synthetic private flag",resolved=index==2,created_at=now-timedelta(hours=age)))
            # Flag review must still see previously flagged records if their catalog
            # or approval state changes; do not add new public-selection rules.
            commodity.is_active=False;market.is_active=False;db.commit()

    def tearDown(self):self.engine.dispose()

    def test_existing_database_reason_limit_rejected_before_storage(self):
        for value in (None,"","x"*50,"é"*50):self.assertEqual(PriceFlagCreate(reason=value).reason,value)
        for value in ("x"*51,"é"*51):
            with self.subTest(length=len(value)),self.assertRaises(ValidationError):PriceFlagCreate(reason=value)

    def test_flag_counts_order_and_original_fields_keep_rejected_inactive_records(self):
        with Session(self.engine) as db:
            result=list_flagged_price_updates(db)
            self.assertEqual([row.price_update_id for row in result],list(reversed(self.ids)))
            self.assertEqual([row.flag_count for row in result],[2,2,2])
            for row in result:
                self.assertEqual(row.commodity_name,"Egusi");self.assertEqual(row.market_name,"Kwali Market")
                self.assertEqual(set(row.model_dump()),{"price_update_id","commodity_name","market_name","flag_count","latest_flag_at"})

    def test_one_query_without_loading_private_price_or_flag_entities_or_changing_history(self):
        with Session(self.engine) as db:
            before={table.name:db.execute(select(table)).all() for table in (PriceUpdate.__table__,PriceFlag.__table__)}
            loaded=[];statements=[];event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(type(instance).__name__))
            def capture(connection,cursor,statement,parameters,context,many):statements.append(statement)
            event.listen(self.engine,"before_cursor_execute",capture);result=list_flagged_price_updates(db);event.remove(self.engine,"before_cursor_execute",capture)
            self.assertEqual(len(result),3);self.assertEqual(len(statements),1);self.assertEqual(loaded,[])
            for table in (PriceUpdate.__table__,PriceFlag.__table__):self.assertEqual(db.execute(select(table)).all(),before[table.name])

    def test_no_open_flags_returns_no_rows(self):
        with Session(self.engine) as db:
            for row in db.scalars(select(PriceFlag)):row.resolved=True
            db.commit();self.assertEqual(list_flagged_price_updates(db),[])
