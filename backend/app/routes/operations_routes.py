"""Private, bounded operational trigger; no browser or customer authentication."""
import base64
import json

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from app.config import get_settings
from app.database import get_engine
from app.services.payment_reconciliation_service import reconcile_payments
from app.services.operations_auth_service import authorize_operation


router = APIRouter(prefix="/internal/operations", include_in_schema=False)
MAX_BODY_BYTES = 8192
MAX_CHECKPOINT_CHARACTERS = 4096
MAX_RECORD_ID = 2_147_483_647
OUTCOMES = ("confirmed", "unconfirmed", "review_required", "error", "missing_record")


def _reject(status: int, detail: str) -> None:
    raise HTTPException(status_code=status, detail=detail, headers={"Cache-Control": "private, no-store"})


def _cipher() -> Fernet:
    secret = get_settings().jwt_secret
    if not isinstance(secret, str) or len(secret) < 32:
        _reject(503, "Operational checkpoint protection is not configured")
    # Distinct purpose: the browser JWT key is never used directly for encryption.
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=b"priceyard-operational-recovery-checkpoint-v1").derive(secret.encode())
    return Fernet(base64.urlsafe_b64encode(key))


def _valid_cursor(after_id: object, ceiling_id: object) -> bool:
    return (type(after_id) is int and type(ceiling_id) is int
            and 0 <= after_id <= ceiling_id <= MAX_RECORD_ID)


def _decode_checkpoint(checkpoint: str | None) -> tuple[int, int | None]:
    if checkpoint is None:
        return 0, None
    try:
        value = json.loads(_cipher().decrypt(checkpoint.encode("ascii")))
        if (not isinstance(value, dict) or set(value) != {"version", "after_id", "ceiling_id"}
                or type(value["version"]) is not int or value["version"] != 1
                or not _valid_cursor(value["after_id"], value["ceiling_id"])):
            raise ValueError("Invalid checkpoint")
        return value["after_id"], value["ceiling_id"]
    except (InvalidToken, ValueError, UnicodeError, TypeError):
        _reject(400, "Invalid operational checkpoint")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate key")
        result[key] = value
    return result


async def _payload(request: Request) -> str | None:
    if request.query_params:
        _reject(400, "Invalid operational request")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        _reject(415, "Operational request requires JSON")
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        _reject(413, "Operational request is too large")
    try:
        payload = json.loads(body, object_pairs_hook=_unique_object)
        if not isinstance(payload, dict) or set(payload) - {"checkpoint"}:
            raise ValueError("Invalid payload")
        checkpoint = payload.get("checkpoint")
        if checkpoint is not None and (not isinstance(checkpoint, str)
                                      or not 1 <= len(checkpoint) <= MAX_CHECKPOINT_CHARACTERS):
            raise ValueError("Invalid checkpoint")
        return checkpoint
    except (ValueError, UnicodeError, TypeError):
        _reject(400, "Invalid operational request")


def _recover(checkpoint: str | None, after_id: int, ceiling_id: int | None) -> dict:
    try:
        report = reconcile_payments(get_engine(), apply=True, limit=25, after_id=after_id,
                                    ceiling_id=ceiling_id, time_budget_seconds=45)
        if (report["dry_run"] is not False or type(report["busy"]) is not bool
                or type(report["complete"]) is not bool or not isinstance(report["outcomes"], list)
                or len(report["outcomes"]) > 25):
            raise ValueError("Invalid recovery result")
        counts = dict.fromkeys(OUTCOMES, 0)
        for item in report["outcomes"]:
            counts[item["outcome"]] += 1
        next_checkpoint = checkpoint
        if not report["busy"]:
            if report["complete"]:
                next_checkpoint = None
            else:
                next_after, next_ceiling = report["next_after_id"], report["ceiling_id"]
                if not _valid_cursor(next_after, next_ceiling):
                    raise ValueError("Invalid recovery cursor")
                value = json.dumps({"version": 1, "after_id": next_after, "ceiling_id": next_ceiling}, separators=(",", ":"))
                next_checkpoint = _cipher().encrypt(value.encode()).decode("ascii")
        return {"busy": report["busy"], "complete": report["complete"],
                "processed": len(report["outcomes"]), "outcomes": counts, "checkpoint": next_checkpoint}
    except Exception:
        # Database URLs, private references and provider bodies never leave this trigger.
        _reject(503, "Operational recovery could not complete")


@router.post("/recover-payments")
async def recover_payments(request: Request) -> JSONResponse:
    await run_in_threadpool(authorize_operation, request)
    checkpoint = await _payload(request)
    _cipher()  # Validate resumable-state protection before any payment work.
    after_id, ceiling_id = _decode_checkpoint(checkpoint)
    report = await run_in_threadpool(_recover, checkpoint, after_id, ceiling_id)
    return JSONResponse(report, headers={"Cache-Control": "private, no-store"})
