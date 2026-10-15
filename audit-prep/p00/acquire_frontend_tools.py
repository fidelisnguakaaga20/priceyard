"""Acquire only declared npm tooling in a clean, app-free directory.

Run separately from all application tests. No lifecycle scripts or dotenv are
loaded, and npm user/global configuration is replaced by empty local files.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "audit-prep/p00"

def main() -> int:
    target = LAB / "runtime" / ("npm-tools-" + uuid.uuid4().hex)
    target.mkdir(parents=True)
    shutil.copyfile(ROOT / "frontend/package.json", target / "package.json")
    for name in ("user.npmrc", "global.npmrc"):
        (target / name).write_text("", encoding="utf-8")
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    env["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"
    env["USERPROFILE"] = str(target)
    env["APPDATA"] = str(target / "appdata")
    env["LOCALAPPDATA"] = str(target / "localappdata")
    command = [r"C:/Program Files/nodejs/node.exe", r"C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js",
               "install", "--prefix", str(target), "--userconfig", str(target / "user.npmrc"),
               "--globalconfig", str(target / "global.npmrc"), "--cache", str(LAB / "runtime/npm-cache"),
               "--registry", "https://registry.npmjs.org", "--ignore-scripts", "--no-audit", "--no-fund"]
    result = subprocess.run(command, cwd=target, env=env, check=False)
    if result.returncode:
        return result.returncode
    shutil.copyfile(target / "package-lock.json", ROOT / "frontend/package-lock.json")
    (LAB / "runtime/frontend-tools.json").write_text(json.dumps({"path": str(target), "purpose": "declared-npm-tooling-no-lifecycle-scripts"}), encoding="utf-8")
    print("Declared frontend tooling acquired; reproducible package-lock recorded.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
