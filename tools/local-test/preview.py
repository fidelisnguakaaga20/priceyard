"""Real original API + original UI, fresh synthetic memory database only."""
import asyncio
from html import escape
import json
import os
import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from unittest.mock import patch

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
from app.models.payment import Payment
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import build_trial_subscription
from app.utils.password import hash_password
from app.main import app as api
from app.services import password_reset_service

local_reset_inbox = []

def capture_reset_message(*, recipient, reset_url):
    if not recipient.endswith("@example.com") or not reset_url.startswith("http://127.0.0.1:55446/reset-password?"):
        raise RuntimeError("Only fabricated local reset messages may be captured")
    local_reset_inbox.append({"recipient": recipient, "reset_url": reset_url})

password_reset_service.send_password_reset_email = capture_reset_message

engine = get_engine()
Base.metadata.create_all(engine)
now = datetime.now(timezone.utc)
with Session(engine) as db:
    users = {}
    demo_hash = hash_password("PriceYardDemo8!")
    for name, role, access in (("free", "free_user", "free"), ("trial", "free_user", "trial"), ("paid", "paid_user", "active"), ("reporter", "reporter", "free"), ("admin", "admin", "free"), ("expired-reporter", "reporter", "trial_expired"), ("expired-paid-reporter", "reporter", "paid_expired"), ("reset", "free_user", "trial"), ("payment", "free_user", "free"), ("manual-paid", "paid_user", "manual_active"), ("value-paid", "paid_user", "active"), ("value-trial", "free_user", "trial"), ("verify", "free_user", "free"), ("referrer", "free_user", "trial")):
        user = User(full_name=f"Test {name.title()}", email=f"{name}@example.com", password_hash=demo_hash, role=role, is_active=True, referral_code="TEST"+name.upper())
        if access in {"trial", "trial_expired"}:
            user.subscription = build_trial_subscription(user=user, now=now-timedelta(days=15) if access == "trial_expired" else now)
        else:
            paid = access in {"active", "paid_expired", "manual_active"}
            user.subscription = Subscription(status="active" if paid else access, plan_name="paid" if access == "manual_active" else "paid_monthly" if paid else "free", start_date=(now-timedelta(days=31)).date() if access == "paid_expired" else now.date() if paid else None, end_date=None if access == "manual_active" else (now-timedelta(days=1)).date() if access == "paid_expired" else (now+timedelta(days=30)).date() if paid else None)
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
    db.add(Payment(user_id=users["payment"].id, reference="py_local_browser_only", plan="monthly", amount=2500, currency="NGN", status="pending"))
    db.add(Payment(user_id=users["value-paid"].id, reference="py_local_renewal_only", plan="monthly", amount=2500, currency="NGN", status="pending"))
    db.add(Payment(user_id=users["value-trial"].id, reference="py_local_trial_purchase_only", plan="seasonal", amount=6000, currency="NGN", status="pending"))
    db.add(Payment(user_id=users["verify"].id, reference="py_local_verify_only", plan="monthly", amount=2500, currency="NGN", status="pending"))
    db.add(Payment(user_id=users["manual-paid"].id, reference="py_local_manual_review_only", plan="monthly", amount=2500, currency="NGN", status="pending"))
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
    return JSONResponse({"synthetic_only": True, "process_id": os.getpid(), "database": "fresh memory SQLite", "providers": "disabled", "grades": False, "fixture": "original Egusi/Kwali Market/1 bag; bag size unknown", "isolation": isolation})

async def push_controls(request):
    return HTMLResponse((LAB / "push_controls.html").read_text(encoding="utf-8"))

async def inbox(request):
    links = "".join('<li><a href="'+escape(item["reset_url"], quote=True)+'">Open reset link for '+escape(item["recipient"])+'</a></li>' for item in local_reset_inbox)
    return HTMLResponse('<!doctype html><html><head><title>Local test inbox</title></head><body style="font:18px system-ui;max-width:760px;margin:32px auto;padding:16px"><h1>Local test inbox</h1><p>Fabricated accounts only. No email was sent. Reset links expire under the original application rules.</p><ul>'+links+'</ul><a href="/forgot-password">Open original password-reset request form</a></body></html>')

async def payment_event(request):
    # Test controls invoke the real webhook via an in-process ASGI transport.
    # The fabricated signing key exists only during this serialized test call;
    # ordinary payment initiation remains disabled by empty provider settings.
    import httpx
    from app.config import get_settings
    from sqlalchemy import select
    payload = await request.json()
    if payload not in ({"event": "wrong_amount"}, {"event": "valid"}, {"event": "activation_failure"}, {"event": "value_paid"}, {"event": "value_trial"}, {"event": "manual_review"}):
        return JSONResponse({"detail": "Choose a fabricated local payment event"}, status_code=400)
    event = {"event": "charge.success", "data": {"reference": "py_local_browser_only", "id": 700001, "amount": 249999 if payload["event"] == "wrong_amount" else 250000, "currency": "NGN", "status": "success"}}
    if payload["event"] == "value_paid":
        event["data"].update(reference="py_local_renewal_only", id=700002)
    elif payload["event"] == "value_trial":
        event["data"].update(reference="py_local_trial_purchase_only", id=700003, amount=600000)
    elif payload["event"] == "manual_review":
        event["data"].update(reference="py_local_manual_review_only", id=700005)
    raw = json.dumps(event).encode()
    key = "sk_test_priceyard_local_browser_only"
    signature = hmac.new(key.encode(), raw, hashlib.sha512).hexdigest()
    fake_settings = get_settings().model_copy(update={"paystack_secret_key": key})
    from contextlib import ExitStack
    with ExitStack() as patches:
        patches.enter_context(patch("app.services.payment_service.get_settings", return_value=fake_settings))
        if payload["event"] == "activation_failure":
            patches.enter_context(patch("app.services.payment_service.activate_paid_subscription", side_effect=RuntimeError("Fabricated local activation failure")))
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=api, raise_app_exceptions=False), base_url="http://synthetic-asgi-only") as client:
            response = await client.post("/payments/webhook", content=raw, headers={"x-paystack-signature": signature})
    with Session(engine) as db:
        payment = db.scalar(select(Payment).where(Payment.reference == event["data"]["reference"]))
        return JSONResponse({"synthetic_only": True, "webhook_status": response.status_code, "payment_status": payment.status, "subscription_status": payment.user.subscription.status, "end_date": str(payment.user.subscription.end_date) if payment.user.subscription.end_date else None})

async def payment_controls(request):
    return HTMLResponse('''<!doctype html><html><head><title>Local payment testing</title></head><body style="font:18px system-ui;max-width:760px;margin:32px auto;padding:16px"><h1>Local payment testing</h1><p>Fabricated payment@example.com account only. Password: PriceYardDemo8! No money is charged and no provider is contacted. These controls are separate from PriceYard.</p><ol><li>Sign in as payment@example.com in <a href="/login" target="_blank">the original application</a>.</li><li>Send the wrong-amount event, then simulate an activation failure. Access must remain Free and payment pending.</li><li>Send the valid event. Reload the original Dashboard to see Active Paid. Repeating it keeps the same expiry.</li></ol><button onclick="sendEvent('wrong_amount')">Send wrong-amount test event</button> <button onclick="sendEvent('activation_failure')">Simulate activation failure</button> <button onclick="sendEvent('valid')">Send valid test event</button><pre id="result" role="status"></pre><script>async function sendEvent(event){const response=await fetch('/__test__/payment-event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({event})});document.querySelector('#result').textContent=JSON.stringify(await response.json(),null,2)}</script></body></html>''')

async def purchase_value_controls(request):
    from sqlalchemy import select
    with Session(engine) as db:
        fixtures = {}
        for name in ("value-paid", "value-trial"):
            user = db.scalar(select(User).where(User.email == name+"@example.com"))
            subscription = user.subscription
            fixtures[name] = {"paid_end": str(subscription.end_date) if subscription.end_date else None,
                              "trial_end": str(subscription.trial_ends_at) if subscription.trial_ends_at else None}
    html = (LAB / "purchase_value_controls.html").read_text(encoding="utf-8")
    return HTMLResponse(html.replace("__STATE__", escape(json.dumps(fixtures, indent=2))))


async def manual_review_controls(request):
    return HTMLResponse((LAB / "manual_review_controls.html").read_text(encoding="utf-8"))

outage = {"enabled": False}
checkout_mode = {"mode": "disabled"}
verification_mode = {"mode": "disabled"}


async def verification_controls(request):
    return HTMLResponse((LAB / "verification_controls.html").read_text(encoding="utf-8"))


async def set_verification_mode(request):
    payload = await request.json()
    if payload not in ({"mode": "disabled"}, {"mode": "pending"}, {"mode": "wrong_amount"}, {"mode": "valid"}):
        return JSONResponse({"detail": "Choose a synthetic verification reply"}, status_code=400)
    verification_mode.update(payload)
    return JSONResponse({"synthetic_only": True, **verification_mode})


async def serve_fake_verification(app, scope, receive, send):
    import requests
    from app.config import get_settings
    def provider(session, method, url, **kwargs):
        if method.upper() != "GET" or url != "https://api.paystack.co/transaction/verify/py_local_verify_only":
            raise RuntimeError("Only the fabricated verification transport is permitted")
        response = requests.Response(); response.status_code = 200
        response._content = json.dumps({"status": True, "data": {"reference": "py_local_verify_only", "id": 700004,
            "amount": 249999 if verification_mode["mode"] == "wrong_amount" else 250000, "currency": "NGN",
            "status": "pending" if verification_mode["mode"] == "pending" else "success"}}).encode()
        return response
    fake_settings = get_settings().model_copy(update={"paystack_secret_key": "sk_test_synthetic_verification_only"})
    with patch("app.services.payment_service.get_settings", return_value=fake_settings), patch("requests.Session.request", autospec=True, side_effect=provider):
        await app(scope, receive, send)


async def checkout_controls(request):
    return HTMLResponse((LAB / "checkout_controls.html").read_text(encoding="utf-8"))


async def set_checkout_mode(request):
    payload = await request.json()
    if payload not in ({"mode": "disabled"}, {"mode": "unsafe_link"}, {"mode": "valid"}):
        return JSONResponse({"detail": "Choose an isolated checkout fixture"}, status_code=400)
    checkout_mode.update(payload)
    return JSONResponse({"synthetic_only": True, **checkout_mode})


async def serve_fake_checkout(app, scope, receive, send):
    # Called only under the synthetic wrapper's request lock. The entire HTTP
    # provider transport is replaced; unknown destinations fail before TCP/DNS.
    import requests
    from app.config import get_settings
    def provider(session, method, url, **kwargs):
        if method.upper() != "POST" or url != "https://api.paystack.co/transaction/initialize":
            raise RuntimeError("Only the fabricated checkout transport is permitted")
        checkout = "https://example.invalid/unsafe-checkout" if checkout_mode["mode"] == "unsafe_link" else "https://checkout.paystack.com/priceyard-synthetic-only"
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({"status": True, "data": {"authorization_url": checkout, "reference": kwargs["json"]["reference"], "access_code": "priceyard-synthetic-only"}}).encode()
        return response
    fake_settings = get_settings().model_copy(update={"paystack_secret_key": "sk_test_synthetic_checkout_only"})
    with patch("app.services.payment_service.get_settings", return_value=fake_settings), patch("requests.Session.request", autospec=True, side_effect=provider):
        await app(scope, receive, send)

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
                if scope.get("path") == "/api/payments/initiate" and checkout_mode["mode"] != "disabled":
                    await serve_fake_checkout(self.app, scope, receive, secured)
                elif scope.get("path") == "/api/payments/py_local_verify_only/verify" and verification_mode["mode"] != "disabled":
                    await serve_fake_verification(self.app, scope, receive, secured)
                else:
                    await self.app(scope, receive, secured)
        else:
            await self.app(scope, receive, secured)

preview = LocalOnly(Starlette(routes=[Route("/__test__/status", status), Route("/__test__/inbox", inbox), Route("/__test__/controls", controls), Route("/__test__/push", push_controls), Route("/__test__/payments", payment_controls), Route("/__test__/manual-review", manual_review_controls), Route("/__test__/purchase-value", purchase_value_controls), Route("/__test__/verification", verification_controls), Route("/__test__/verification-mode", set_verification_mode, methods=["POST"]), Route("/__test__/checkout", checkout_controls), Route("/__test__/checkout-mode", set_checkout_mode, methods=["POST"]), Route("/__test__/payment-event", payment_event, methods=["POST"]), Route("/__test__/outage", control, methods=["POST"]), Mount("/api", app=api), Mount("/", app=PreviewFiles(directory=str(snapshot / "dist")))]))

if __name__ == "__main__":
    import uvicorn
    print("LOCAL_TEST_READY http://127.0.0.1:55446", flush=True)
    uvicorn.run(preview, host="127.0.0.1", port=55446, access_log=False, log_level="warning")
