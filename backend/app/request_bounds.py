"""Bound HTTP input before JSON parsing, database work or provider calls."""
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


MAX_REQUEST_BODY_BYTES = 4 * 1024 * 1024
MAX_REQUEST_TARGET_BYTES = 8 * 1024
MAX_REQUEST_HEADER_BYTES = 64 * 1024


class RequestBoundsMiddleware:
    def __init__(self, app: ASGIApp, *, max_body_bytes: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def reject(status: int, detail: str) -> None:
            # Never echo supplied headers, tokens, body fragments or source data.
            await JSONResponse({"detail": detail}, status_code=status)(scope, receive, send)

        path = scope.get("raw_path")
        if path is None:
            decoded_path = scope.get("path", "")
            if len(decoded_path) > MAX_REQUEST_TARGET_BYTES:
                await reject(414, "Request URL is too long")
                return
            path = decoded_path.encode("utf-8")
        query = scope.get("query_string", b"")
        if len(path) + len(query) + bool(query) > MAX_REQUEST_TARGET_BYTES:
            await reject(414, "Request URL is too long")
            return

        header_bytes = 0
        lengths = []
        for name, value in scope.get("headers", []):
            header_bytes += len(name) + len(value) + 4
            if header_bytes > MAX_REQUEST_HEADER_BYTES:
                await reject(431, "Request headers are too large")
                return
            if name.lower() == b"content-length":
                lengths.append(value.strip())
        if len(lengths) > 1 or (lengths and (not lengths[0].isdigit() or len(lengths[0]) > 19)):
            await reject(400, "Invalid request length")
            return
        declared = int(lengths[0]) if lengths else None
        if declared is not None and declared > self.max_body_bytes:
            await reject(413, "Request body is too large")
            return

        # A bytearray also bounds memory for adversarial one-byte chunks. Buffer
        # before calling the application: even handlers that ignore their body
        # must not save a record before a later oversized chunk is discovered.
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                await reject(400, "Invalid request body")
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_body_bytes:
                await reject(413, "Request body is too large")
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        if declared is not None and declared != len(body):
            await reject(400, "Invalid request length")
            return
        captured = bytes(body)
        body.clear()
        replayed = False

        async def replay() -> Message:
            nonlocal replayed
            if replayed:
                return await receive()
            replayed = True
            return {"type": "http.request", "body": captured, "more_body": False}

        await self.app(scope, replay, send)
