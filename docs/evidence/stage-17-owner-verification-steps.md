# Stage 17 Owner Verification Steps

From the Stage 17 backend folder:

```bash
python -m pip install -r requirements-dev.txt
python -m alembic current
python ../docs/evidence/stage-17-owner-smoke.py
```

Expected Alembic head remains:

```text
0005_stage13_watchlists
```

Expected final smoke line:

```text
STAGE 17 OWNER SMOKE: PASS
```

Do not start Stage 18 until the owner proof passes and approval is given.
