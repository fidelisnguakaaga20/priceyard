"""Build original/current source using existing tools in a credential-free copy."""
import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import uuid
import socket

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(__file__).resolve().parent
RUNTIME = LAB / "runtime"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse", action="store_true", help="Rebuild the marked isolated snapshot without copying dependencies again")
    options = parser.parse_args()
    if options.reuse:
        # Never update a snapshot being served, or build during native testing.
        for port in (55446, 55448):
            with socket.socket() as probe:
                probe.settimeout(1)
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("Stop local preview/PostgreSQL before reusing the test build")
        ready_marker = RUNTIME / "frontend.json"
        progress_marker = RUNTIME / "frontend.reuse-in-progress.json"
        # A failed build deliberately leaves no ready marker. Resume only its
        # preserved identity, with the same port/path/purpose checks below.
        manifest = json.loads((ready_marker if ready_marker.exists() else progress_marker).read_text())
        target = Path(manifest["path"]).resolve()
        if (manifest.get("purpose") != "synthetic-only-no-application-credentials"
                or target.parent != RUNTIME.resolve() or not target.name.startswith("frontend-")
                or not (target / "node_modules").is_dir() or (target / "node_modules").is_symlink()):
            raise RuntimeError("Only the existing marked workspace test snapshot may be reused")
        # Fail closed while updating: a failed build cannot serve the old output
        # as though it had verified the new source. Preserve the previous marker.
        if ready_marker.exists():
            ready_marker.replace(progress_marker)
    else:
        target = RUNTIME / ("frontend-" + uuid.uuid4().hex)
        target.mkdir(parents=True)
    source = ROOT / "frontend"
    for name in ("package.json", "index.html", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "vite.config.ts"):
        shutil.copyfile(source / name, target / name)
    for name in (("src", "public") if options.reuse else ("src", "public", "node_modules")):
        if options.reuse:
            source_files = {item.relative_to(source / name) for item in (source / name).rglob("*") if item.is_file()}
            snapshot_files = {item.relative_to(target / name) for item in (target / name).rglob("*") if item.is_file()}
            if snapshot_files - source_files:
                raise RuntimeError("Snapshot contains removed source files; prepare a reviewed clean snapshot instead")
        shutil.copytree(source / name, target / name, dirs_exist_ok=options.reuse, ignore=lambda path, names: [item for item in names if item.startswith(".env") or item in {".cache", ".vite"} or Path(path, item).is_symlink()])
    env = {name: os.environ[name] for name in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if name in os.environ}
    env.update(VITE_API_URL="/api", VITE_GOOGLE_CLIENT_ID="", NODE_ENV="production")
    node = r"C:\Program Files\nodejs\node.exe"
    for arguments in ([str(target / "node_modules/typescript/bin/tsc"), "-b"], [str(target / "node_modules/vite/bin/vite.js"), "build", "--mode", "synthetic"]):
        result = subprocess.run([node, "--require", str(LAB / "node_guard.cjs"), *arguments], cwd=target, env=env)
        if result.returncode:
            return result.returncode
    manifest = {"path": str(target), "purpose": "synthetic-only-no-application-credentials"}
    staged = RUNTIME / "frontend.next.json"
    staged.write_text(json.dumps(manifest))
    staged.replace(RUNTIME / "frontend.json")
    print(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
