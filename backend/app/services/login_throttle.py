"""Per-account brake on password guessing.

After MAX_FAILURES wrong passwords for the same email within WINDOW_SECONDS, password
login for that email pauses for LOCK_SECONDS. Counting is per account (not per IP),
so it still works behind Render's proxy. State is kept in memory for the single API
process: it resets on restart and needs no database change.
"""

from __future__ import annotations

from collections import deque
import threading
import time

MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60
LOCK_SECONDS = 15 * 60
_MAX_TRACKED = 10_000  # bound memory if someone sprays many different emails

_failures: dict[str, deque[float]] = {}
_locked_until: dict[str, float] = {}
_lock = threading.Lock()


def _prune(now: float) -> None:
    for key in [k for k, until in _locked_until.items() if until <= now]:
        del _locked_until[key]
    for key in list(_failures):
        attempts = _failures[key]
        while attempts and attempts[0] <= now - WINDOW_SECONDS:
            attempts.popleft()
        if not attempts:
            del _failures[key]


def seconds_locked(email: str, now: float | None = None) -> int:
    """Seconds left on this account's pause, or 0 when password login is allowed."""
    now = time.monotonic() if now is None else now
    with _lock:
        until = _locked_until.get(email)
        if until is None:
            return 0
        if until <= now:
            del _locked_until[email]
            return 0
        return max(1, int(until - now + 0.999))


def record_failure(email: str, now: float | None = None) -> None:
    now = time.monotonic() if now is None else now
    with _lock:
        if len(_failures) >= _MAX_TRACKED:
            _prune(now)
        attempts = _failures.setdefault(email, deque())
        while attempts and attempts[0] <= now - WINDOW_SECONDS:
            attempts.popleft()
        attempts.append(now)
        if len(attempts) >= MAX_FAILURES:
            _locked_until[email] = now + LOCK_SECONDS
            attempts.clear()


def clear(email: str) -> None:
    """Forget failures for this account (successful login or password reset)."""
    with _lock:
        _failures.pop(email, None)
        _locked_until.pop(email, None)


def reset_all() -> None:
    """Test helper: forget every account's failures and pauses."""
    with _lock:
        _failures.clear()
        _locked_until.clear()
