# Stage 11 Owner Verification Steps

From `priceyard/backend` with the same working `.env` used for the previous verified stage:

```bash
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python ../docs/evidence/stage-11-owner-smoke.py
```

Expected Alembic head:

```text
0003_stage11_storage_suitability
```

Expected final smoke line:

```text
STAGE 11 OWNER SMOKE: PASS
```

Stage 12 must not start until this proof passes and the owner approves progression.
