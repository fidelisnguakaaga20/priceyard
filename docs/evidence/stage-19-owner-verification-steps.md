# Stage 19 Owner Verification

From the cumulative Stage 19 project root after copying the previous stage `backend/.env`:

```bash
python docs/evidence/stage-19-owner-smoke.py
```

Expected final automated line:

```text
STAGE 19 OWNER SMOKE: PASS
```

The helper runs the real frontend npm install/build, the Stage 19 static route/scope check, verifies a normal user is blocked from admin APIs, and verifies the admin dashboard/management data sources using a temporary API-test admin that is cleaned up automatically.

For the short manual browser rendering check, create a temporary admin:

```bash
python docs/evidence/stage-19-browser-admin.py
```

Use the printed email/password to log in locally, then confirm:
1. The `Admin` navigation link opens `/admin`.
2. The approved dashboard metrics render.
3. `Admin → Price updates` shows editable Possible Meaning and Suggested Action controls.
4. One additional management section such as Commodities or FAQ renders its form/list normally.

Do not create permanent business data with this temporary account. After the visual check, run the exact cleanup command printed by the helper.

Do not start Stage 20 until automated proof, manual rendering proof and owner approval are complete.
