"""Real original API + original UI, fresh synthetic memory database only."""
import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import guard
guard.isolate()

isolation = json.loads((LAB / "runtime/isolation.json").read_text())
if isolation != {"checks": 6, "failures": 0, "errors": 0, "dotenv_contents_opened": False, "production_contacts": 0}:
    raise RuntimeError("Passing isolation verification is required")
manifest = json.loads((LAB / "runtime/frontend.json").read_text())
snapshot = Path(manifest["path"]).resolve()
if manifest.get("purpose") != "synthetic-only-no-application-credentials" or not snapshot.is_relative_to((LAB / "runtime").resolve()):
    raise RuntimeError("Unapproved frontend build")

from sqlalchemy.orm import Session
from app.database import Base, get_engine
import app.models
from app.models.commodity import Commodity
from app.models.faq_item import FAQItem
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password
from app.main import app as api

engine = get_engine()
Base.metadata.create_all(engine)
now = datetime.now(timezone.utc)
with Session(engine) as db:
    users = {}
    demo_hash = hash_password("PriceYardDemo8!")
    for name, role, access in (("free", "free_user", "free"), ("trial", "free_user", "trial"), ("paid", "paid_user", "active"), ("reporter", "reporter", "free"), ("admin", "admin", "free"), ("expired-reporter", "reporter", "trial_expired"), ("expired-paid-reporter", "reporter", "paid_expired")):
        user = User(full_name=f"Test {name.title()}", email=f"{name}@example.com", password_hash=demo_hash, role=role, is_active=True, referral_code="TEST"+name.upper())
        if access in {"trial", "trial_expired"}:
            user.subscription = build_trial_subscription(user=user, now=now-timedelta(days=15) if access == "trial_expired" else now)
        else:
            paid = access in {"active", "paid_expired"}
            user.subscription = Subscription(status="active" if paid else access, plan_name="paid_monthly" if paid else "free", start_date=(now-timedelta(days=31)).date() if access == "paid_expired" else now.date() if paid else None, end_date=(now-timedelta(days=1)).date() if access == "paid_expired" else (now+timedelta(days=30)).date() if paid else None)
        db.add(user)
        users[name] = user
    commodity = Commodity(name="Egusi", is_active=True)
    market = Market(name="Kwali Market", state="FCT", country="Nigeria", market_day="Tuesday", is_active=True)
    db.add_all([commodity, market])
    db.flush()
    for day, low in ((1, 210000), (0, 211000)):
        # Existing original unit from test_watchlist_alert_service.py. Unknown
        # bag_size stays NULL. No invented grades or quantity conversions.
        db.add(PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=low, price_high=low+10000, average_price=low+5000, previous_price_low=210000 if day == 0 else None, previous_price_high=220000 if day == 0 else None, unit="1 bag", bag_size=None, movement="up" if day == 0 else "unknown", confidence_level="Low confidence", update_date_time=now-timedelta(days=day), status="approved", created_by=users["admin"].id, approved_by=users["admin"].id, notes="Fabricated local test price; bag size not supplied.", source_1="LOCAL-PRIVATE-SOURCE"))
    db.add(FAQItem(question="Local testing question", answer="Fabricated test entry only.", category="Local testing", is_published=True, created_by=users["admin"].id))
    db.commit()

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

class PreviewFiles(StaticFiles):
    async def get_response(self, path, scope):
        current = json.loads((LAB / "runtime/frontend.json").read_text())
        current_snapshot = Path(current["path"]).resolve()
        if current.get("purpose") != "synthetic-only-no-application-credentials" or not current_snapshot.is_relative_to((LAB / "runtime").resolve()):
            raise RuntimeError("Unapproved frontend build")
        if path in {"sw.js", "service-worker.js"}:
            return JSONResponse({"local_test": "Service workers disabled for uncached review"}, status_code=404)
        if path in {"", "."} or path.endswith("/") or "." not in Path(path).name:
            html = (current_snapshot / "dist/index.html").read_text(encoding="utf-8")
            notice = '<aside style="padding:6px 12px;background:#fff3c4;color:#352600;font:14px system-ui" role="status">LOCAL TEST ONLY — fabricated accounts/prices; real payments and messages disabled.</aside>'
            safety = '''<script>window.open=()=>null;if(navigator.share)navigator.share=async()=>{throw Error('Disabled in local test')};if(window.Notification)Notification.requestPermission=async()=> 'denied';if(window.PushManager)PushManager.prototype.subscribe=async()=>{throw Error('Disabled in local test')};if(navigator.serviceWorker)navigator.serviceWorker.register=async()=>{throw Error('Disabled in local test')};document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[href]');if(a&&new URL(a.href,location.href).origin!==location.origin){e.preventDefault();alert('External links are disabled in local testing.')}},true);</script>'''
            return HTMLResponse(html.replace("<body>", "<body>"+notice+safety))
        return await StaticFiles(directory=str(current_snapshot / "dist")).get_response(path, scope)

async def status(request):
    return JSONResponse({"synthetic_only": True, "database": "fresh memory SQLite", "providers": "disabled", "grades": False, "fixture": "original Egusi/Kwali Market/1 bag; bag size unknown", "isolation": isolation})

outage = {"enabled": False}

async def control(request):
    payload = await request.json()
    if set(payload) != {"enabled"} or not isinstance(payload["enabled"], bool):
        return JSONResponse({"detail": "Expected one boolean enabled value"}, status_code=400)
    outage["enabled"] = payload["enabled"]
    return JSONResponse(outage)

async def controls(request):
    return HTMLResponse('''<!doctype html><html><head><title>PriceYard local testing controls</title></head><body style="font:18px system-ui;max-width:760px;margin:32px auto;padding:16px"><h1>Local testing controls</h1><p>These controls affect fabricated local test prices only. They are separate from the PriceYard application.</p><ol><li>Click <b>Simulate connection problem</b>.</li><li>Open <a href="/" target="_blank">the homepage</a> in another tab. Its existing error message should appear.</li><li>Return here and click <b>Restore connection</b>.</li><li>Return to the homepage. With Data saver Off, the normal refresh should show prices and remove the error within one minute.</li></ol><button onclick="setOutage(true)">Simulate connection problem</button> <button onclick="setOutage(false)">Restore connection</button><p id="status" role="status"></p><script>async function setOutage(enabled){const response=await fetch('/__test__/outage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled})});if(!response.ok)throw Error('Control failed');document.querySelector('#status').textContent=enabled?'Simulated price outage enabled.':'Connection restored. Prices will refresh normally.'}</script></body></html>''')

class LocalOnly:
    def __init__(self, app):
        self.app = app
        # SQLite StaticPool shares a memory connection. Serialize fixture HTTP
        # requests; this preview is not evidence of production concurrency.
        self.request_lock = asyncio.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            if headers.get(b"host") != b"127.0.0.1:55446" or headers.get(b"origin", b"http://127.0.0.1:55446") != b"http://127.0.0.1:55446":
                return await JSONResponse({"detail": "Local test only"}, status_code=403)(scope, receive, send)
            test_client = headers.get(b"x-priceyard-test-client", b"").decode("ascii", errors="ignore")
            if test_client:
                if not re.fullmatch(r"[a-zA-Z0-9-]{1,64}", test_client):
                    return await JSONResponse({"detail": "Invalid test identity"}, status_code=400)(scope, receive, send)
                # Separate fabricated browser clients, retaining real per-client
                # login limits. This header exists only in the local wrapper.
                scope = dict(scope, client=("local-test-"+test_client, 0))
        async def secured(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend([(b"cache-control", b"no-store"), (b"content-security-policy", b"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'")])
            await send(message)
        if scope["type"] == "http" and scope.get("path") == "/api/price-updates" and outage["enabled"]:
            return await JSONResponse({"detail": "Synthetic temporary outage"}, status_code=503)(scope, receive, secured)
        if scope["type"] == "http":
            async with self.request_lock:
                await self.app(scope, receive, secured)
        else:
            await self.app(scope, receive, secured)

preview = LocalOnly(Starlette(routes=[Route("/__test__/status", status), Route("/__test__/controls", controls), Route("/__test__/outage", control, methods=["POST"]), Mount("/api", app=api), Mount("/", app=PreviewFiles(directory=str(snapshot / "dist")))]))

if __name__ == "__main__":
    import uvicorn
    print("LOCAL_TEST_READY http://127.0.0.1:55446", flush=True)
    uvicorn.run(preview, host="127.0.0.1", port=55446, access_log=False, log_level="warning")
