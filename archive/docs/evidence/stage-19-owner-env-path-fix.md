# Stage 19 owner smoke environment-path fix

Owner attempt on 2026-08-13 stopped before Stage 19 tests with:
`RuntimeError: DATABASE_URL is required for database operations`.

Cause: `backend/app/config.py` intentionally resolves `.env` relative to the current working directory. The Stage 19 owner helper is launched from the project root, while the approved secret file is `backend/.env`, so app settings were imported before the helper entered the backend runtime directory.

Smallest fix: `docs/evidence/stage-19-owner-smoke.py` now changes its working directory to `backend/` before importing application modules. No application code, API, schema, migration, dependency, or Stage 20 behavior changed.

Assistant verification:
- helper Python compilation: PASS
- Stage 19 static scope check: PASS
- backend `.env` resolution behavior with a temporary non-secret test DATABASE_URL: PASS

Owner must rerun the Stage 19 smoke with the real copied `backend/.env`. Stage 19 remains IN PROGRESS until that proof and the required manual admin-browser check pass.
