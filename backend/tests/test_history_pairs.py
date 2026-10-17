from datetime import datetime, timedelta, timezone
import unittest

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.schemas.price_update_schema import PriceHistoryPair
from app.services.price_update_service import list_price_history, list_price_history_pairs


class HistoryPairsTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user=User(full_name="Synthetic metadata Admin",email="history-pairs@example.com",password_hash="unused",role="admin",referral_code="HISTORYPAIR")
            commodities=[Commodity(name=name,is_active=name!="Palm oil") for name in ("Egusi","Honey Beans","Palm oil")]
            market=Market(name="Kwali Market");db.add_all([user,market,*commodities]);db.flush();self.market_id=market.id
            now=datetime.now(timezone.utc)
            for index,(commodity,status,outdated) in enumerate([(commodities[0],"approved",True)]*100+[(commodities[1],"approved",False),(commodities[1],"pending",False),(commodities[2],"approved",False)]):
                db.add(PriceUpdate(commodity_id=commodity.id,market_id=market.id,unit="1 bag",bag_size=None,
                    price_low=210000,price_high=220000,movement="unknown",confidence_level="Low confidence",
                    status=status,is_outdated=outdated,created_by=user.id,update_date_time=now-timedelta(hours=index),source_1="PRIVATE-PAIR-SOURCE"))
            db.commit()

    def tearDown(self):self.engine.dispose()

    def test_distinct_options_match_all_existing_active_approved_history_including_outdated(self):
        with Session(self.engine) as db:
            expected=sorted({(row.commodity.name,row.market.name) for row in list_price_history(db)})
            pairs=list_price_history_pairs(db)
            self.assertEqual([(row["commodity"]["name"],row["market"]["name"]) for row in pairs],expected)
            self.assertEqual(len(pairs),2)
            for row in pairs:
                self.assertEqual(PriceHistoryPair.model_validate(row).model_dump(),row)
                self.assertNotIn("PRIVATE",str(row));self.assertNotIn("price_low",str(row))

    def test_one_query_no_entity_hydration_or_history_changes(self):
        with Session(self.engine) as db:
            table=PriceUpdate.__table__;before=db.execute(select(table)).all();loaded=[];statements=[]
            event.listen(db,"loaded_as_persistent",lambda session,instance:loaded.append(instance))
            def capture(connection,cursor,statement,parameters,context,many):statements.append(statement)
            event.listen(self.engine,"before_cursor_execute",capture)
            self.assertEqual(len(list_price_history_pairs(db)),2)
            event.remove(self.engine,"before_cursor_execute",capture)
            self.assertEqual(len(statements),1);self.assertIn("DISTINCT",statements[0]);self.assertEqual(loaded,[])
            self.assertEqual(db.execute(select(table)).all(),before)

    def test_inactive_market_is_excluded_without_deleting_its_history(self):
        with Session(self.engine) as db:
            db.get(Market,self.market_id).is_active=False;db.commit()
            self.assertEqual(list_price_history_pairs(db),[])
            self.assertEqual(len(db.scalars(select(PriceUpdate.id)).all()),103)

    def test_empty_history_has_no_pairs(self):
        engine=create_engine("sqlite+pysqlite:///:memory:");Base.metadata.create_all(engine)
        try:
            with Session(engine) as db:self.assertEqual(list_price_history_pairs(db),[])
        finally:engine.dispose()
