"""Synthetic original API for the virtual HTTPS browser, stdio only, no sockets."""
import base64
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import guard
guard.isolate()
sys.path.insert(0, str(guard.BACKEND / 'tests'))
from test_render_routing_contract import LocalRewriteModel, FRONT
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password

settings = get_settings()
settings.app_env = 'staging'
settings.frontend_url = settings.cors_origins = FRONT
engine = create_engine('sqlite+pysqlite:///:memory:')
Base.metadata.create_all(engine)
with Session(engine) as db:
    user = User(full_name='Synthetic Routing', email='routing@example.com',
                password_hash=hash_password('SyntheticRouting8!'), role='free_user',
                is_active=True, referral_code='ROUTING')
    user.subscription = build_trial_subscription(user=user)
    db.add(user)
    db.commit()

def sessions():
    with Session(engine, expire_on_commit=False) as db:
        yield db

app.dependency_overrides[get_db] = sessions
client = TestClient(LocalRewriteModel(app), base_url=FRONT, raise_server_exceptions=False)
print(json.dumps({'ready': True, 'scope': 'synthetic in-process API; DNS TCP providers and dotenv denied'}), flush=True)
try:
    for line in sys.stdin:
        item = json.loads(line)
        target = urlsplit(item['url'])
        if target.scheme != 'https' or target.netloc != 'priceyard.onrender.com' or not target.path.startswith('/api/'):
            raise RuntimeError('Only the fixed virtual same-origin API is permitted')
        # Let the browser alone supply cookies; no invisible TestClient cookie jar.
        client.cookies.clear()
        response = client.request(item['method'], item['url'], headers=item['headers'],
                                  content=base64.b64decode(item['body']), follow_redirects=False)
        print(json.dumps({'id': item['id'], 'status': response.status_code,
                          'headers': list(response.headers.multi_items()),
                          'body': base64.b64encode(response.content).decode()}), flush=True)
finally:
    client.close()
    engine.dispose()
