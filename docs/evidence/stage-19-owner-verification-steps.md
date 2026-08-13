# Stage 19 Owner Verification

From the cumulative Stage 19 project root after copying the previous stage `backend/.env`:

```bash
python docs/evidence/stage-19-owner-smoke.py
```

Expected final automated line:

```text
STAGE 19 OWNER SMOKE: PASS
```

The helper runs the real frontend npm install/build, the Stage 19 static route/scope check, verifies a normal user is blocked from admin APIs, and verifies the admin dashboard/management data sources using a temporary admin account that is cleaned up automatically.

Manual owner check before approval:
1. Sign in with an existing admin account.
2. Confirm the `Admin` navigation link opens `/admin`.
3. Confirm the dashboard metrics render.
4. Open at least Price updates and verify Possible Meaning + Suggested Action edit controls render.
5. Open one additional management section (for example Commodities or FAQ) and confirm the form/list layout is usable.

Do not start Stage 20 until both automated and manual proof are accepted by the owner.
