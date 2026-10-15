"""Inspect installed tooling without importing application modules or secrets."""
import importlib.util
import json
import sys
from pathlib import Path

print(json.dumps({"python": sys.version.split()[0], "packages": {
    name: importlib.util.find_spec(name) is not None
    for name in ("pip", "venv", "fastapi", "sqlalchemy", "httpx")
}}))
