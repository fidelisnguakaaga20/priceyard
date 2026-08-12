# Stage 4 Owner Verification Steps

Run from `priceyard/backend` after setting `JWT_SECRET` in `.env`:

```bash
python -m pip install -r requirements-dev.txt
python ../docs/evidence/stage-4-owner-smoke.py
```

Expected final line:

```text
STAGE 4 OWNER SMOKE: PASS
```

The smoke test uses the configured PostgreSQL database, creates a uniquely named temporary user, verifies the approved Stage 4 authentication behaviors, and deletes the temporary user before exit.
