from __future__ import annotations

import json
import logging
import ipaddress
import socket
import secrets
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from fastapi import HTTPException, status
from pywebpush import WebPushException, webpush
import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.util.connection import create_connection
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate, validate_push_endpoint

logger = logging.getLogger(__name__)
MAX_PUSH_DEVICES = 10
_DNS_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="priceyard-push-dns")


def public_push_addresses(host: str) -> list[str]:
    # Bound caller latency and the number of outstanding OS resolver calls.
    future = _DNS_EXECUTOR.submit(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM)
    try:
        records = future.result(timeout=3)
    except FutureTimeoutError:
        future.cancel()
        raise ValueError("Push provider lookup timed out") from None
    addresses = list(dict.fromkeys(record[4][0] for record in records))
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise ValueError("Push provider must resolve only to public addresses")
    return sorted(addresses, key=lambda value: ipaddress.ip_address(value).version)


class SafePushSession(requests.Session):
    """Pin a checked public address while retaining provider TLS hostname/SNI."""

    def __init__(self) -> None:
        super().__init__()
        self.trust_env = False

    def request(self, method, url, **kwargs):
        validate_push_endpoint(url)
        addresses = public_push_addresses(urlsplit(url).hostname)
        pinned_address = addresses[0]

        class PinnedConnection(HTTPSConnection):
            def _new_conn(connection):
                return create_connection((pinned_address, connection.port), timeout=connection.timeout,
                                         source_address=connection.source_address, socket_options=connection.socket_options)

        class PinnedPool(HTTPSConnectionPool):
            ConnectionCls = PinnedConnection

        class PinnedAdapter(HTTPAdapter):
            def init_poolmanager(adapter, *args, **options):
                super().init_poolmanager(*args, **options)
                adapter.poolmanager.pool_classes_by_scheme = dict(adapter.poolmanager.pool_classes_by_scheme, https=PinnedPool)

        self.mount("https://", PinnedAdapter(max_retries=0))
        kwargs.update(allow_redirects=False, timeout=(3.05, 10), proxies={}, verify=True)
        return super().request(method, url, **kwargs)


def save_subscription(db: Session, user: User, payload: PushSubscriptionCreate) -> PushSubscription:
    # Serialize per-account device limits with account security changes.
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    existing = db.scalar(select(PushSubscription).where(PushSubscription.endpoint == payload.endpoint))
    count = db.scalar(select(func.count()).select_from(PushSubscription).where(PushSubscription.user_id == user.id)) or 0
    if existing is not None:
        if existing.user_id != user.id:
            if not secrets.compare_digest(existing.p256dh, payload.keys.p256dh) or not secrets.compare_digest(existing.auth, payload.keys.auth):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Notification endpoint ownership could not be confirmed")
            if count >= MAX_PUSH_DEVICES:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Maximum notification devices reached")
        existing.user_id = user.id
        existing.p256dh = payload.keys.p256dh
        existing.auth = payload.keys.auth
        db.flush()
        return existing

    if count >= MAX_PUSH_DEVICES:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Maximum notification devices reached; remove an unused device first")

    subscription = PushSubscription(
        user_id=user.id,
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
    )
    db.add(subscription)
    db.flush()
    return subscription


def remove_subscription(db: Session, user: User, endpoint: str) -> None:
    db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.endpoint == endpoint,
    ).delete()
    db.flush()


def send_push_to_user(db: Session, user_id: int, *, title: str, body: str, url: str) -> int:
    """Bounded device delivery; retry transient failures through the worker.

    All devices in the batch are attempted. Dead endpoints are pruned. Retrying a
    partial failure can duplicate an earlier successful device delivery.
    """
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        return 0
    subscriptions = list(db.scalars(select(PushSubscription).where(PushSubscription.user_id == user_id)).all())
    if not subscriptions:
        return 0
    settings = get_settings()
    if not settings.vapid_public_key or not settings.vapid_private_key:
        raise RuntimeError("Push delivery is not configured")

    payload = json.dumps({"title": title, "body": body, "url": url}, ensure_ascii=False)
    if len(payload.encode("utf-8")) > 3500:
        raise ValueError("Push message exceeds supported size")
    sent = 0
    failed = False
    # Existing excess devices are retained, but a job must fit its bounded lease.
    for subscription in subscriptions[:MAX_PUSH_DEVICES]:
        try:
            validate_push_endpoint(subscription.endpoint)
            with SafePushSession() as transport:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                    },
                    data=payload,
                    vapid_private_key=settings.vapid_private_key,
                    vapid_claims={"sub": f"mailto:{settings.vapid_claim_email}"},
                    timeout=10,
                    requests_session=transport,
                )
            sent += 1
        except WebPushException as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code in (404, 410):
                db.delete(subscription)
                db.flush()
            else:
                failed = True
                logger.warning("Push send failed for subscription %s", subscription.id)
        except Exception as exc:
            failed = True
            logger.warning("Push send failed for subscription %s (%s)", subscription.id, type(exc).__name__)
    if failed:
        raise RuntimeError("Push delivery temporarily failed for one or more devices")
    return sent
