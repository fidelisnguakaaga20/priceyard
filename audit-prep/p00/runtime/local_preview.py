"""Disposable real-API preview: synthetic SQLite only; never load real dotenv."""
from pathlib import Path
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parents[1]
spec = importlib.util.spec_from_file_location("priceyard_preview_isolation", LAB / "run_backend_tests.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
guard.isolate()

manifest = json.loads((LAB / "runtime/frontend-snapshot.json").read_text(encoding="utf-8"))
snapshot = Path(manifest["path"]).resolve()
if manifest.get("purpose") != "secret-free-synthetic-frontend-build" or not snapshot.is_relative_to((LAB / "source-snapshot").resolve()):
    raise RuntimeError("Unapproved preview source")
dist = snapshot / "dist"
if not (dist / "index.html").is_file():
    raise RuntimeError("A verified synthetic build is required")

from sqlalchemy.orm import Session
from app.database import Base, get_engine
import app.models
from app.models.user import User
from app.models.subscription import Subscription
from app.models.commodity import Commodity
from app.models.market import Market
from app.schemas.price_update_schema import PriceUpdateCreate
from app.utils.password import hash_password
from app.services.price_update_service import create_price_update, approve_price_update
from app.services.subscription_service import build_trial_subscription
from app.main import app as api

engine = get_engine()
Base.metadata.create_all(engine)
now = datetime.now(timezone.utc)
password = "PriceYardDemo8!"
with Session(engine, expire_on_commit=False) as db:
    users = {}
    for label, role, access in [("free", "free_user", "free"), ("trial", "free_user", "trial"), ("paid", "paid_user", "active"), ("reporter", "reporter", "free"), ("admin", "admin", "free")]:
        user = User(full_name=f"Demo {label.title()}", email=f"{label}@example.com", password_hash=hash_password(password), role=role, is_active=True, email_verified=True, referral_code="DEMO"+label.upper())
        user.subscription = build_trial_subscription(user=user) if access == "trial" else Subscription(status=access, plan_name="paid_monthly" if access == "active" else "free", paid_expires_at=now+timedelta(days=30) if access == "active" else None)
        db.add(user)
        users[label] = user
    db.flush()
    market = Market(name="Demo market (synthetic)", state="FCT", country="Nigeria", is_active=True)
    crops = [Commodity(name=name, description="Illustrative synthetic prices for local demonstration only.", is_active=True) for name in ("Egusi", "Honey Beans", "Palm oil")]
    db.add_all([market, *crops]); db.commit()
    for crop_index, crop in enumerate(crops):
        for package_index, (bag, grade) in enumerate((("50kg", "A"), ("25kg", "B"))):
            for day in range(4):
                low = 25000 + crop_index*10000 + package_index*3000 + day*1000
                item = create_price_update(db, PriceUpdateCreate(commodity_id=crop.id, market_id=market.id,
                    price_low=low, price_high=low+2000, average_price=low+1000,
                    unit="1 bag", bag_size=bag, grade=grade, movement="unknown",
                    confidence_level="Low confidence", update_date_time=now-timedelta(days=3-day),
                    suggested_action="Watch", possible_meaning="DEMO: illustrative observation, not a real market recommendation.",
                    notes="Synthetic demonstration record."), users["admin"])
                approve_price_update(db, item, users["admin"])
    db.commit()

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

class PreviewFiles(StaticFiles):
    async def get_response(self, path, scope):
        from starlette.exceptions import HTTPException
        if path == "" or path == "." or path.endswith("/") or "." not in Path(path).name:
            html = (dist / "index.html").read_text(encoding="utf-8")
            banner = '''<aside style="background:#fff3c4;color:#352600;padding:12px;font:14px system-ui;border-bottom:2px solid #9c7b00" role="status"><strong>LOCAL DEMO - SYNTHETIC DATA ONLY</strong><br>Live payments and messaging are disabled. Demo emails: free@example.com, trial@example.com, paid@example.com, reporter@example.com, admin@example.com. Password for all: <strong>PriceYardDemo8!</strong></aside>'''
            script = '''<script>try{window.open=function(u){if(new URL(u||'/',location.href).origin!==location.origin){alert('External links are disabled in this demo.');return null;}return null;};if(navigator.share)navigator.share=async function(){throw new Error('Sharing disabled in local demo');};if(window.Notification)Notification.requestPermission=async function(){return 'denied';};if(window.PushManager)PushManager.prototype.subscribe=async function(){throw new Error('Push disabled in local demo');};}catch(e){}document.addEventListener('click',function(e){const a=e.target.closest&&e.target.closest('a[href]');if(a&&new URL(a.href,location.href).origin!==location.origin){e.preventDefault();alert('External links are disabled in this local demo.');}},true);</script>'''
            return HTMLResponse(html.replace('<body>', '<body>'+banner+script))
        try:
            return await super().get_response(path, scope)
        except HTTPException:
            raise

preview = Starlette(routes=[Mount("/api", app=api), Mount("/", app=PreviewFiles(directory=str(dist)))])
class LocalOnly:
    def __init__(self, app): self.app=app
    async def __call__(self, scope, receive, send):
        headers=dict(scope.get('headers',[]))
        if scope.get('type')=='http' and (headers.get(b'host')!=b'127.0.0.1:55442' or headers.get(b'origin',b'http://127.0.0.1:55442')!=b'http://127.0.0.1:55442'):
            from starlette.responses import PlainTextResponse
            await PlainTextResponse('Local synthetic preview only',status_code=403)(scope,receive,send)
            return
        async def secure_send(message):
            if message['type']=='http.response.start':
                message.setdefault('headers',[]).extend([
                    (b'content-security-policy', b"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'"),
                    (b'x-priceyard-preview', b'synthetic-local-only'), (b'cache-control',b'no-store')])
            await send(message)
        await self.app(scope,receive,secure_send)

if __name__ == '__main__':
    import uvicorn
    print('LOCAL_PREVIEW_READY http://127.0.0.1:55442/prices', flush=True)
    print('Real application API; synthetic in-memory data; external transports denied; no worker or real payments.', flush=True)
    uvicorn.run(LocalOnly(preview), host='127.0.0.1', port=55442, access_log=False, log_level='warning', workers=1)
