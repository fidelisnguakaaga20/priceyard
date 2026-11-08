from pathlib import Path

config = Path("backend/app/config.py").read_text(encoding="utf-8")
main = Path("backend/app/main.py").read_text(encoding="utf-8")
env_example = Path("backend/.env.example").read_text(encoding="utf-8")
api = Path("frontend/src/services/api.ts").read_text(encoding="utf-8")
gitignore = Path(".gitignore").read_text(encoding="utf-8")

checks = {
    "CORS setting exists": 'cors_origins: str = ""' in config,
    "CORS middleware imported": "from fastapi.middleware.cors import CORSMiddleware" in main,
    "CORS origins are environment-derived": "settings.cors_origins.split" in main,
    "CORS middleware uses exact list": "allow_origins=allowed_origins" in main,
    "CORS wildcard origin is absent": 'allow_origins=["*"]' not in main,
    "credentials are disabled": "allow_credentials=False" in main,
    "production debug defaults false": "debug: bool = False" in config,
    "environment example documents CORS": "CORS_ORIGINS=" in env_example,
    "frontend supports deployed API URL": "VITE_API_URL" in api,
    "env files remain ignored": ".env" in gitignore,
}

failed = []
for label, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {label}")
    if not passed:
        failed.append(label)

if failed:
    raise SystemExit("STAGE 22 DEPLOYMENT PREP: FAIL")

print("STAGE 22 DEPLOYMENT PREP: PASS")
