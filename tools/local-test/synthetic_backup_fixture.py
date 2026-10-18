"""Tiny current-schema business fixture; imported only by pinned native runner."""
from datetime import datetime,timedelta,timezone
import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base
from app.models.audit_log import AuditLog
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.payment import Payment
from app.models.price_update import PriceUpdate
from app.models.revoked_access_token import RevokedAccessToken
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import build_trial_subscription


def prepare_backup_fixture(check,engine,schema,lab):
    marker=lab/'runtime/synthetic-backup-fixture.json'
    if marker.exists():raise RuntimeError('Preserve existing recovery evidence; do not create another fixture')
    Base.metadata.create_all(engine);now=datetime.now(timezone.utc)
    with Session(engine) as db:
        users=[]
        for name,role in [('admin','admin'),('paid','paid_user'),('trial','free_user')]:
            user=User(full_name='Synthetic recovery '+name,email='recovery-'+name+'@example.com',role=role,
                password_hash='synthetic-not-a-customer-password',referral_code='REST'+name.upper(),auth_version=1)
            user.subscription=build_trial_subscription(user=user,now=now) if name=='trial' else Subscription(
                plan_name='paid_monthly' if name=='paid' else 'free',status='active' if name=='paid' else 'free',
                start_date=now.date() if name=='paid' else None,end_date=(now+timedelta(days=40)).date() if name=='paid' else None)
            users.append(user)
        commodity=Commodity(name='Egusi');market=Market(name='Kwali Market')
        db.add_all([*users,commodity,market]);db.flush()
        for plan,amount,status in [('monthly',2500,'success'),('seasonal',6000,'pending')]:
            db.add(Payment(user_id=users[1].id,reference='py_synthetic_restore_'+plan,plan=plan,amount=amount,
                currency='NGN',status=status,paystack_transaction_id='synthetic-evidence-'+plan))
        for index in range(2):
            db.add(PriceUpdate(commodity_id=commodity.id,market_id=market.id,created_by=users[0].id,
                price_low=210000+index,price_high=220000+index,unit='1 bag',bag_size=None,commodity_type=None,
                movement='unknown',confidence_level='Low confidence',status='approved',
                source_1='SYNTHETIC-PRIVATE-RECOVERY',notes='Synthetic historical note',
                update_date_time=now-timedelta(days=index)))
        db.add(AuditLog(user_id=users[0].id,action='local.synthetic_recovery',table_name='subscriptions',record_id=users[1].subscription.id,
            old_value={'status':'trial'},new_value={'status':'active','preserved_days':40}))
        db.add(RevokedAccessToken(token_hash=hashlib.sha256(b'synthetic-revoked-recovery-token').hexdigest(),
            user_id=users[1].id,expires_at=now+timedelta(days=90),revoked_at=now))
        db.commit()
        check.assertEqual(len(db.scalars(select(User)).all()),3)
        check.assertEqual(users[2].subscription.trial_ends_at-users[2].subscription.trial_started_at,timedelta(days=14))
        check.assertEqual(users[1].subscription.end_date,(now+timedelta(days=40)).date())
    manifest={'purpose':'synthetic-only-backup-recovery-20261018','source_database':'priceyard_isolated_test',
        'target_database':'priceyard_synthetic_restore_20261018','schema':schema,'host':'127.0.0.1','port':55449,
        'system_identifier':'7697910732590408300','synthetic_business_rows':14}
    with marker.open('x',encoding='utf-8') as output:json.dump(manifest,output,indent=2)
