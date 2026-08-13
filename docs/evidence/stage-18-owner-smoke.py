"""Stage 18 owner verification helper.

Run from the project root after backend/.env has been copied into this stage.
This uses the owner's real backend configuration, builds the React frontend,
starts FastAPI + Vite locally, verifies the API proxy and SPA route availability.
Visual browser/mobile proof remains an explicit manual owner check because repeated
Windows Chrome headless screenshot runs were nondeterministic even while the app
and API were healthy.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def run(command: list[str], cwd: Path) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def wait_json(url: str, timeout: float = 30.0) -> dict:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - smoke helper
            last = exc
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}: {last}")


def wait_text(url: str, timeout: float = 30.0) -> str:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                return response.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}: {last}")


def main() -> None:
    if not (BACKEND / ".env").exists():
        raise SystemExit("FAIL: backend/.env is missing. Copy it from Stage 17 first.")
    npm = "npm.cmd" if os.name == "nt" else "npm"
    if not shutil.which(npm):
        raise SystemExit("FAIL: npm is not available.")

    run([npm, "install"], FRONTEND)
    run([npm, "run", "build"], FRONTEND)
    assert (FRONTEND / "dist" / "index.html").exists()
    print("frontend production build: PASS")

    backend_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=BACKEND)
    frontend_proc = subprocess.Popen([npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"], cwd=FRONTEND)
    try:
        health = wait_json("http://127.0.0.1:8000/health")
        assert health == {"status": "healthy"}
        print("FastAPI health: PASS")
        proxied = wait_json("http://127.0.0.1:5173/api/health")
        assert proxied == {"status": "healthy"}
        print("Vite -> FastAPI API proxy: PASS")
        html = wait_text("http://127.0.0.1:5173/")
        assert '<div id="root"></div>' in html
        print("frontend dev server: PASS")

        routes = [
            "/",
            "/prices",
            "/history",
            "/market-days",
            "/faq",
            "/login",
            "/register",
            "/commodities/Egusi",
        ]
        for route in routes:
            route_html = wait_text(f"http://127.0.0.1:5173{route}")
            assert '<div id="root"></div>' in route_html
            print(f"frontend SPA route {route}: PASS")

        print(
            "AUTOMATED VISUAL SCREENSHOT: SKIPPED "
            "(manual owner browser/mobile proof required)"
        )
    finally:
        frontend_proc.terminate(); backend_proc.terminate()
        try: frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired: frontend_proc.kill()
        try: backend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired: backend_proc.kill()

    print("STAGE 18 OWNER SMOKE: PASS")
    print("MANUAL OWNER CHECK STILL REQUIRED: register/login, add/remove watchlist, submit feedback, open /commodities/Egusi, and confirm 375px mobile layout has no horizontal panning before approval.")


if __name__ == "__main__":
    main()
