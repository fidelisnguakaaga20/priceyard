"""Copy only allowlisted source to a secret-free, disposable frontend workspace."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "audit-prep" / "p00"
SOURCE = ROOT / "frontend"
NODE = Path(r"C:/Program Files/nodejs/node.exe")

def snapshot() -> Path:
    target = LAB / "source-snapshot" / ("frontend-" + uuid.uuid4().hex)
    target.mkdir(parents=True)
    for name in ("package.json", "package-lock.json", "index.html", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "vite.config.ts"):
        source = SOURCE / name
        if source.is_file():
            shutil.copyfile(source, target / name)
    for name in ("src", "public", "tests", "node_modules"):
        source = SOURCE / name
        if name == "node_modules" and (LAB / "runtime/frontend-tools.json").is_file():
            tool = json.loads((LAB / "runtime/frontend-tools.json").read_text(encoding="utf-8"))
            tool_path = Path(tool["path"]).resolve()
            if tool.get("purpose") != "declared-npm-tooling-no-lifecycle-scripts" or not tool_path.is_relative_to((LAB / "runtime").resolve()):
                raise RuntimeError("Unapproved frontend tooling path")
            if (tool_path / "package.json").read_bytes() != (SOURCE / "package.json").read_bytes():
                raise RuntimeError("Tooling does not match declared frontend dependencies; reacquire first")
            source = tool_path / name
        if not source.is_dir():
            raise RuntimeError(f"Required local tooling/source missing: {name}")
        def ignore(path, names):
            return [item for item in names if item.startswith(".env") or item in {".cache", ".vite"} or Path(path, item).is_symlink()]
        shutil.copytree(source, target / name, ignore=ignore)
    (LAB / "runtime").mkdir(exist_ok=True)
    (LAB / "runtime" / "frontend-snapshot.json").write_text(json.dumps({"path": str(target), "purpose": "secret-free-synthetic-frontend-build"}), encoding="utf-8")
    return target

def run(target: Path, arguments: list[str]) -> int:
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    env.update(VITE_API_URL="/api", VITE_DEV_API_TARGET="http://127.0.0.1:55440", VITE_GOOGLE_CLIENT_ID="", NODE_ENV="production")
    process = subprocess.run([str(NODE), "--require", str(LAB / "node_transport_guard.cjs"), *arguments], cwd=target, env=env, check=False)
    return process.returncode

def main() -> int:
    target = snapshot()
    # Build/test tools run from this copy; Vite cannot discover the real .env.
    print(json.dumps({"snapshot": str(target), "production_credentials": "absent"}), flush=True)
    if run(target, ["--test", *[str(p) for p in sorted((target / "tests").glob("*.test.mjs"))]]) != 0:
        return 1
    if run(target, [str(target / "node_modules/typescript/bin/tsc"), "-b"]) != 0:
        return 1
    return run(target, [str(target / "node_modules/vite/bin/vite.js"), "build", "--mode", "synthetic"])

if __name__ == "__main__":
    raise SystemExit(main())
