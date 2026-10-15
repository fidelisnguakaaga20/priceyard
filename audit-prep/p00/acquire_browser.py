"""Download the matching Playwright headless browser only, without app config."""
import json
import os
from pathlib import Path
import subprocess

LAB = Path(__file__).resolve().parent
def main():
    manifest = json.loads((LAB / "runtime/frontend-tools.json").read_text(encoding="utf-8"))
    tools_path = Path(manifest["path"]).resolve()
    if not tools_path.is_relative_to((LAB / "runtime").resolve()) or manifest.get("purpose") != "declared-npm-tooling-no-lifecycle-scripts":
        raise RuntimeError("Unapproved toolchain")
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    env["USERPROFILE"] = str(LAB / "runtime/browser-download-profile")
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(LAB / "runtime/browser-binaries")
    Path(env["USERPROFILE"]).mkdir(exist_ok=True)
    command = [r"C:/Program Files/nodejs/node.exe", str(tools_path / "node_modules/playwright/cli.js"), "install", "chromium", "--only-shell"]
    return subprocess.run(command, env=env, cwd=tools_path, check=False).returncode
if __name__ == "__main__":
    raise SystemExit(main())
