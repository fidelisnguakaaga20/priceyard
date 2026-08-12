# Stage 6 Owner Verification Steps

From `priceyard/backend`, with the same working `.env` used in Stages 3–5:

```bash
python -m pip install -r requirements-dev.txt
python ../docs/evidence/stage-6-owner-smoke.py
```

Expected final line:

```text
STAGE 6 OWNER SMOKE: PASS
```

The verifier leaves the approved initial commodities and markets in PostgreSQL. It removes only temporary test users and temporary CRUD records.
