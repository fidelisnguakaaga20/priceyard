from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Mount
import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.revoked_access_token import RevokedAccessToken
from app.rate_limit import limiter
from app.security import create_access_token, decode_access_claims
from app.services.browser_session_service import SECURE_COOKIE, session_metadata
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password


def verify_browser_sessions(check, engine):
    Base.metadata.create_all(engine)
    password='SyntheticCookie8!'
    with Session(engine) as db:
        user=User(full_name='Synthetic cookie user',email='cookie@example.com',password_hash=hash_password(password),role='free_user',referral_code='COOKIE')
        user.subscription=build_trial_subscription(user=user)
        db.add(user);db.commit();user_id=user.id
    def sessions():
        with Session(engine,expire_on_commit=False) as db: yield db
    app.dependency_overrides[get_db]=sessions
    limiter.reset()
    origin=get_settings().frontend_url
    client=TestClient(app,base_url='https://testserver',raise_server_exceptions=False)
    headers={'Origin':origin}
    payload={'email':'cookie@example.com','password':password,'remember':True}
    try:
        for rejected in ({},{'Origin':'https://untrusted.example.invalid'}):
            with patch('app.routes.auth_routes.authenticate_user',side_effect=AssertionError('Origin must precede authentication')):
                check.assertEqual(client.post('/auth/browser/login',json=payload,headers=rejected).status_code,403)
        login=client.post('/auth/browser/login',json=payload,headers=headers)
        check.assertEqual(login.status_code,200,login.text)
        metadata=login.json();check.assertEqual(set(metadata),{'session_id','csrf_token'})
        cookie=login.headers['set-cookie'];raw=client.cookies.get(SECURE_COOKIE)
        for attribute in ('HttpOnly','Secure','SameSite=lax','Path=/','Max-Age='): check.assertIn(attribute,cookie)
        check.assertNotIn('Domain=',cookie)
        check.assertLessEqual(int(cookie.split('Max-Age=')[1].split(';')[0]),90*86400)
        check.assertNotIn(raw,login.text)
        check.assertEqual(client.get('/auth/me').status_code,200)
        check.assertEqual(client.get('/auth/me').headers['cache-control'],'private, no-store')
        check.assertEqual(client.get('/auth/me',headers={'Authorization':'Bearer invalid'}).status_code,401)
        check.assertEqual(client.get('/auth/browser/session').json(),metadata)
        good={**headers,'X-PriceYard-CSRF':metadata['csrf_token'],'X-PriceYard-Session':metadata['session_id']}
        for rejected in (headers,{**good,'Origin':'https://untrusted.example.invalid'},{**good,'X-PriceYard-CSRF':'wrong'}):
            check.assertEqual(client.post('/auth/logout',headers=rejected).status_code,403)
            check.assertEqual(client.get('/auth/me').status_code,200)
        check.assertEqual(client.post('/auth/logout',headers={**good,'X-PriceYard-Session':'old-session'}).status_code,401)
        check.assertEqual(client.cookies.get(SECURE_COOKIE),raw)
        # Reset/disable revocation applies to cookie transport too.
        with Session(engine) as db:
            db.get(User,user_id).auth_version+=1;db.commit()
        check.assertEqual(client.get('/auth/me').status_code,401)
        client.cookies.clear();limiter.reset()
        login=client.post('/auth/browser/login',json={**payload,'remember':False},headers=headers)
        check.assertEqual(login.status_code,200,login.text)
        check.assertNotIn('Max-Age=',login.headers['set-cookie']);check.assertNotIn('expires=',login.headers['set-cookie'].lower())
        raw=client.cookies.get(SECURE_COOKIE);metadata=login.json()
        independent=create_access_token(user_id=user_id,auth_version=1)
        good={**headers,'X-PriceYard-CSRF':metadata['csrf_token'],'X-PriceYard-Session':metadata['session_id']}
        check.assertEqual(client.post('/auth/logout',headers=good).status_code,204)
        check.assertIsNone(client.cookies.get(SECURE_COOKIE))
        with patch.object(get_settings(),'app_env','production'):
            with TestClient(app,base_url='http://127.0.0.1:55446',raise_server_exceptions=False) as plain:
                limiter.reset()
                response=plain.post('/auth/browser/login',json=payload,headers=headers)
                check.assertEqual(response.status_code,200,response.text)
                check.assertIn(SECURE_COOKIE+'=',response.headers['set-cookie'])
                check.assertIn('Secure',response.headers['set-cookie'])
                check.assertNotIn('priceyard_local_session',response.headers['set-cookie'])
                check.assertEqual(plain.get('/auth/me').status_code,401)
        check.assertEqual(client.get('/auth/me',headers={'Authorization':'Bearer '+raw}).status_code,401)
        check.assertEqual(client.get('/auth/me',headers={'Authorization':'Bearer '+independent}).status_code,200)
        # Existing valid JS tokens convert with the identical signed expiry.
        now=datetime.now(timezone.utc)
        legacy=jwt.encode({'sub':str(user_id),'iat':now,'exp':now+timedelta(days=3),'auth_version':1},get_settings().jwt_secret,algorithm='HS256')
        upgraded=client.post('/auth/browser/upgrade',json={'remember':True},headers={**headers,'Authorization':'Bearer '+legacy})
        check.assertEqual(upgraded.status_code,200,upgraded.text)
        check.assertEqual(client.cookies.get(SECURE_COOKIE),legacy)
        check.assertEqual(decode_access_claims(client.cookies.get(SECURE_COOKIE))['exp'],decode_access_claims(legacy)['exp'])
        # Replacing browser sign-in revokes the previous cookie, not API clients.
        replacement=client.post('/auth/browser/login',json=payload,headers=headers)
        check.assertEqual(replacement.status_code,200,replacement.text)
        check.assertEqual(client.get('/auth/me',headers={'Authorization':'Bearer '+legacy}).status_code,401)
        check.assertEqual(client.get('/auth/me',headers={'Authorization':'Bearer '+independent}).status_code,200)
        with Session(engine) as db:
            check.assertTrue(all(row.token_hash not in (raw,legacy,independent) for row in db.scalars(select(RevokedAccessToken))))
        # New endpoint does not double the existing password guessing quota.
        client.cookies.clear();limiter.reset()
        for index in range(6):
            response=client.post('/auth/browser/login' if index%2 else '/auth/login',headers=headers,
                json={'email':'absent@example.com','password':'wrong-password'})
            check.assertEqual(response.status_code,429 if index==5 else 401,response.text)
        preflight=client.options('/auth/me',headers={'Origin':origin,'Access-Control-Request-Method':'GET'})
        check.assertEqual(preflight.headers['access-control-allow-origin'],origin)
        check.assertEqual(preflight.headers['access-control-allow-credentials'],'true')
        rejected=client.options('/auth/me',headers={'Origin':'https://untrusted.example.invalid','Access-Control-Request-Method':'GET'})
        check.assertNotIn('access-control-allow-origin',rejected.headers)
        with TestClient(Starlette(routes=[Mount('/api',app=app)]),base_url='https://testserver') as mounted:
            response=mounted.get('/api/auth/browser/session')
            check.assertEqual(response.status_code,401)
            check.assertEqual(response.headers['cache-control'],'private, no-store')
        expired=jwt.encode({'sub':str(user_id),'iat':now-timedelta(days=2),'exp':now-timedelta(days=1),'auth_version':1},get_settings().jwt_secret,algorithm='HS256')
        client.cookies.set(SECURE_COOKIE,expired,domain='testserver.local',path='/')
        expired_meta=session_metadata(expired)
        removed=client.post('/auth/logout',headers={**headers,'X-PriceYard-CSRF':expired_meta['csrf_token'],'X-PriceYard-Session':expired_meta['session_id']})
        check.assertEqual(removed.status_code,204,removed.text)
        check.assertIsNone(client.cookies.get(SECURE_COOKIE))
    finally:
        client.close();app.dependency_overrides.clear();limiter.reset()


class BrowserSessionTests(unittest.TestCase):
    def test_cookie_csrf_legacy_revocation_and_bearer_compatibility(self):
        engine=create_engine('sqlite+pysqlite:///:memory:')
        try:verify_browser_sessions(self,engine)
        finally:engine.dispose()
