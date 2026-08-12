# Stage 7 Owner Verification Steps

From `priceyard/backend`, with the same private `.env` used for the owner-verified Supabase PostgreSQL database:

```bash
python -m pip install -r requirements-dev.txt
python ../docs/evidence/stage-7-owner-smoke.py
```

Expected final line:

```text
STAGE 7 OWNER SMOKE: PASS
```

The verifier tests only Stage 7 Price Updates and cleans up temporary price/user/subscription records. It relies on the owner-verified Stage 6 core `Egusi` commodity and `Nasarawa` market records.
