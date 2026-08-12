# Stage 10 Owner Verification Steps

Stage 10 adds two approved tables, so apply the migration before running the owner smoke test.

From `priceyard/backend`:

```bash
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python ../docs/evidence/stage-10-owner-smoke.py
```

Expected migration target:

```text
0002_stage10_buy_sell_watch
```

Expected final smoke line:

```text
STAGE 10 OWNER SMOKE: PASS
```

Do not proceed to Stage 11 until this local/Supabase-backed test passes and the owner approves Stage 11.
