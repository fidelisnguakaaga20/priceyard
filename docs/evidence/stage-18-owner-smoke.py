"""Stage 18 owner verification helper.

Run from the project root after backend/.env has been copied into this stage.
This uses the owner's real backend configuration, builds the React frontend,
starts FastAPI + Vite locally, verifies the API proxy and browser rendering,
and writes a mobile-width screenshot into docs/evidence.

It intentionally does not install a new browser automation dependency.
Chrome/Chromium is invoked in headless mode when available.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
EVIDENCE = ROOT / "docs" / "evidence"


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


def find_chrome() -> str | None:
    candidates = [
        shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser"),
        os.environ.get("PROGRAMFILES", "") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("PROGRAMFILES(X86)", "") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("LOCALAPPDATA", "") + r"\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def chrome_base_args(chrome: str, profile_dir: str) -> list[str]:
    return [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-sync",
        "--metrics-recording-only",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={profile_dir}",
    ]


def browser_screenshot(chrome: str, route: str, output: Path, width: int = 1440, height: int = 1000) -> None:
    output.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="priceyard-stage18-chrome-") as profile_dir:
        command = chrome_base_args(chrome, profile_dir) + [
            "--virtual-time-budget=3000",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            f"--screenshot={output}",
            f"http://127.0.0.1:5173{route}",
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            process.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            # Some Windows Chrome builds write the screenshot successfully but keep
            # a background process alive. Stop it and judge the browser proof by
            # the screenshot artifact rather than by Chrome's exit timing.
            process.kill()
            process.communicate()

    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"Chrome did not produce a browser screenshot for {route}")


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

        chrome = find_chrome()
        if not chrome:
            raise RuntimeError("Chrome/Chromium not found for browser/mobile verification")
        routes = ["/", "/prices", "/history", "/market-days", "/faq", "/login", "/register"]
        with tempfile.TemporaryDirectory(prefix="priceyard-stage18-routes-") as route_dir:
            route_dir_path = Path(route_dir)
            for index, route in enumerate(routes):
                route_shot = route_dir_path / f"route-{index}.png"
                browser_screenshot(chrome, route, route_shot)
                print(f"browser route {route}: PASS")

        screenshot = EVIDENCE / "stage-18-owner-mobile.png"
        browser_screenshot(chrome, "/prices", screenshot, width=390, height=844)
        print("390x844 mobile-width browser render: PASS")
        print("Mobile screenshot:", screenshot)
    finally:
        frontend_proc.terminate(); backend_proc.terminate()
        try: frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired: frontend_proc.kill()
        try: backend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired: backend_proc.kill()

    print("STAGE 18 OWNER SMOKE: PASS")
    print("MANUAL OWNER CHECK STILL REQUIRED: register/login, add/remove watchlist, submit feedback, and visually inspect the mobile screenshot before approval.")


if __name__ == "__main__":
    main()
