from datetime import datetime, timedelta, timezone
import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.services.price_update_service import list_latest_approved_price_updates, list_market_comparison, list_price_history


class CurrentSpecificationTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        self.now=datetime(2026,10,17,9,tzinfo=timezone.utc)
        with Session(self.engine) as db:
            admin=User(full_name="Synthetic price specification",email="specifications@example.com",password_hash="unused",role="admin",referral_code="SPECS")
            commodity,market=Commodity(name="Egusi"),Market(name="Kwali Market");db.add_all([admin,commodity,market]);db.flush()
            self.admin_id,self.commodity_id,self.market_id=admin.id,commodity.id,market.id;db.commit()

    def tearDown(self):self.engine.dispose()

    def add(self,db,age,**changes):
        values=dict(commodity_id=self.commodity_id,market_id=self.market_id,unit="1 bag",bag_size=None,commodity_type=None,
                    price_low=210000,price_high=220000,status="approved",movement="unknown",confidence_level="Low confidence",
                    update_date_time=self.now-timedelta(hours=age),created_by=self.admin_id)
        item=PriceUpdate(**{**values,**changes});db.add(item);db.flush();return item.id

    def test_distinct_recorded_quantities_and_types_are_not_silently_replaced(self):
        with Session(self.engine) as db:
            # Arbitrary strings exercise existing free-text fields, not recommended
            # commodity weights, new grades, conversions or production fixtures.
            first=self.add(db,4,unit="recorded quantity one",bag_size="recorded size one",commodity_type="recorded type one")
            other_quantity=self.add(db,3,unit="recorded quantity two",bag_size="recorded size one",commodity_type="recorded type one")
            other_size=self.add(db,2,unit="recorded quantity one",bag_size="recorded size two",commodity_type="recorded type one")
            other_type=self.add(db,1,unit="recorded quantity one",bag_size="recorded size one",commodity_type="recorded type two")
            current=self.add(db,0,unit=" RECORDED QUANTITY ONE ",bag_size=" RECORDED SIZE ONE ",commodity_type=" RECORDED TYPE ONE ");db.commit()
            self.assertEqual([row.id for row in list_latest_approved_price_updates(db)],[current,other_type,other_size,other_quantity])
            self.assertNotIn(first,[row.id for row in list_latest_approved_price_updates(db)])
            self.assertEqual(len(list_price_history(db)),5)
            self.assertEqual({row.id for row in list_market_comparison(db,commodity_search="Egusi")},{current,other_type,other_size,other_quantity})

    def test_outdated_or_movement_filter_does_not_resurface_old_same_specification(self):
        with Session(self.engine) as db:
            self.add(db,3,movement="up");latest=self.add(db,1,is_outdated=True,movement="down")
            other=self.add(db,2,unit="another recorded quantity",movement="up");db.commit()
            self.assertEqual([row.id for row in list_latest_approved_price_updates(db)],[other])
            self.assertEqual([row.id for row in list_latest_approved_price_updates(db,movement="up")],[other])
            self.assertEqual(len(list_price_history(db)),3);self.assertTrue(db.get(PriceUpdate,latest).is_outdated)

    def test_unknown_values_remain_unknown_and_historical_business_fields_unchanged(self):
        with Session(self.engine) as db:
            self.add(db,1);self.add(db,0,bag_size="Unknown");db.commit()
            before=db.execute(select(PriceUpdate.__table__)).all()
            rows=list_latest_approved_price_updates(db)
            self.assertEqual({row.bag_size for row in rows},{None,"Unknown"})
            self.assertEqual(db.execute(select(PriceUpdate.__table__)).all(),before)
