"""Build original/current source using existing tools in a credential-free copy."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(__file__).resolve().parent
RUNTIME = LAB / "runtime"


def main():
    target = RUNTIME / ("frontend-" + uuid.uuid4().hex)
    target.mkdir(parents=True)
    source = ROOT / "frontend"
    for name in ("package.json", "index.html", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "vite.config.ts"):
        shutil.copyfile(source / name, target / name)
    for name in ("src", "public", "node_modules"):
        shutil.copytree(source / name, target / name, ignore=lambda path, names: [item for item in names if item.startswith(".env") or item in {".cache", ".vite"} or Path(path, item).is_symlink()])
    env = {name: os.environ[name] for name in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if name in os.environ}
    env.update(VITE_API_URL="/api", VITE_GOOGLE_CLIENT_ID="", NODE_ENV="production")
    node = r"C:\Program Files\nodejs\node.exe"
    for arguments in ([str(target / "node_modules/typescript/bin/tsc"), "-b"], [str(target / "node_modules/vite/bin/vite.js"), "build", "--mode", "synthetic"]):
        result = subprocess.run([node, "--require", str(LAB / "node_guard.cjs"), *arguments], cwd=target, env=env)
        if result.returncode:
            return result.returncode
    manifest = {"path": str(target), "purpose": "synthetic-only-no-application-credentials"}
    (RUNTIME / "frontend.json").write_text(json.dumps(manifest))
    print(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
