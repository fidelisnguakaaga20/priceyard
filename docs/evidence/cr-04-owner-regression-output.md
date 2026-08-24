# CR-04 Owner Automated Regression Output

Date: 2026-08-24

## Result

Automated regression: RETESTED/PASS.

Final read-only browser verification remains required before CR-04 approval.

## Commands and results

### Focused source checks

- `node docs/evidence/cr-01-static-check.mjs` — `CR-01 STATIC CHECK: PASS`.
- `node docs/evidence/cr-02-static-check.mjs` — `CR-02 STATIC CHECK: PASS`.
- `python docs/evidence/cr-03-static-check.py` — `CR-03 STATIC CHECK: PASS`.

### Frontend production build

- `npm run build` — PASS.
- TypeScript build completed.
- Vite 5.4.11 transformed 71 modules and built successfully in 2.64 seconds.

### Configured PostgreSQL/API regression

- `python ../docs/evidence/cr-04-owner-regression.py fidelisnguakaaga20@gmail.com`
- Database migration remained `0006_cr03_egusi_kwali`.
- Egusi and Kwali Market remained the only active public records.
- Public prices contained no inactive references.
- Admin and normal-user authentication/access checks passed.
- Trial, active, free, expired, cancelled and inactive access checks passed.
- Admin commodity/market/price flows passed using temporary records.
- Feedback boundary/privacy/summary checks passed.
- All temporary records were cleaned.
- Fallback cleanup completed.
- Final line: `CR-04 OWNER REGRESSION: PASS`.

## Safety

No password, JWT, database URL or secret is recorded. The test changed no schema or application source and removed its temporary business records.
