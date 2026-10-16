"""Scrubbed launch using already installed local browser tools."""
import os
from pathlib import Path
import subprocess
import sys

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[1]
env = {name: os.environ[name] for name in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if name in os.environ}
env["PLAYWRIGHT_BROWSERS_PATH"] = str(ROOT / ".git/priceyard-local-recovery-20261015/p00/runtime/browser-binaries")
script = sys.argv[1] if len(sys.argv) > 1 else "browser_checks.mjs"
if Path(script).name != script or not script.endswith(".mjs"):
    raise RuntimeError("Only local browser check scripts accepted")
raise SystemExit(subprocess.call([r"C:\Program Files\nodejs\node.exe", "--require", str(LAB / "node_guard.cjs"), str(LAB / script)], cwd=LAB, env=env))
