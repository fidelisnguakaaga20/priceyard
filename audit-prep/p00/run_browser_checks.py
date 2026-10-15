"""Fresh browser profile; use only secret-free snapshot and synthetic routes."""
import json
import os
from pathlib import Path
import subprocess
import sys

LAB = Path(__file__).resolve().parent

def main():
    manifest = json.loads((LAB / "runtime/frontend-snapshot.json").read_text(encoding="utf-8"))
    snapshot = Path(manifest["path"]).resolve()
    if manifest.get("purpose") != "secret-free-synthetic-frontend-build" or not snapshot.is_relative_to((LAB / "source-snapshot").resolve()):
        raise RuntimeError("Unapproved browser source path")
    if not (snapshot / "dist/index.html").is_file():
        raise RuntimeError("A successful secret-free build is required first")
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    env.update(USERPROFILE=str(LAB / "runtime/browser-profile-base"), APPDATA=str(LAB / "runtime/browser-appdata"), LOCALAPPDATA=str(LAB / "runtime/browser-localappdata"))
    for key in ("USERPROFILE", "APPDATA", "LOCALAPPDATA"):
        Path(env[key]).mkdir(parents=True, exist_ok=True)
    temporary = LAB / "runtime/browser-temp"
    temporary.mkdir(exist_ok=True)
    env["TEMP"] = env["TMP"] = str(temporary)
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(LAB / "runtime/browser-binaries")
    if sys.argv[1:] not in ([], ["--pwa"]):
        raise RuntimeError("Only the fixed synthetic workflow or PWA suite is supported")
    script = "browser_pwa.mjs" if sys.argv[1:] else "browser_smoke.mjs"
    if sys.argv[1:]:
        env["PRICEYARD_PWA_TEST"] = "isolated-loopback"
    command = [r"C:/Program Files/nodejs/node.exe", "--require", str(LAB / "node_transport_guard.cjs"), str(LAB / script), str(snapshot)]
    return subprocess.run(command, cwd=snapshot, env=env, check=False).returncode

if __name__ == "__main__":
    raise SystemExit(main())
