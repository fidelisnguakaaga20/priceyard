# CR-04 Regression Testing — Build Report

Date: 2026-08-24

## Current result

Regression helper implementation/syntax, focused CR-01/02/03 checks, frontend production build, and configured PostgreSQL/API regression: RETESTED/PASS.

Owner browser/runtime verification: PASS. CR-04 is RETESTED/PASS and owner-approved.

## Coverage

The focused owner helper verifies:

- backend health, public prices and active-data filtering;
- registration, duplicate email, correct/wrong login, JWT/profile safety;
- 14-day trial and trial/active/free/expired/cancelled access behavior;
- inactive-user and non-admin blocking;
- admin user/subscription/catalog/history/feedback access;
- temporary commodity, market and Egusi/Kwali price create/approve/outdate/cleanup;
- feedback rating validation, submission, privacy, filter and summary;
- final public Egusi/Kwali-only state.

Existing CR-01, CR-02 and CR-03 source checks cover spinner/popup colors, overlays, completion behavior and active-data query/UI contracts. The Vite production build and owner browser checklist provide compiled and visual regression evidence.

## Files

- Added `docs/evidence/cr-04-owner-regression.py`.
- Added `docs/evidence/cr-04-owner-verification-steps.md`.
- Added this build report and helper compile proof.
- Updated governance evidence/status only.

## Scope confirmation

No application source, API contract, database schema/data migration, dependency, access rule, subscription rule, disclaimer, Stage 0–20 feature or deferred feature was changed. CR-04 is verification-only.


## First owner run — failure and smallest fix

- Frontend production build: PASS (71 modules, Vite build completed).
- CR-02 and CR-03 focused checks: PASS.
- CR-01 checker: false FAIL because it required a literal `finally` in Login/Register. CR-02 intentionally uses explicit `setBusy(false)` in both success and error paths before popup display; the checker now verifies both occurrences without changing application code.
- CR-04 helper: owner interrupted after more than 20 minutes with no progress output after the password prompt. The helper now prints each phase/PASS immediately and applies a helper-only 15-second PostgreSQL connection timeout, allowing the exact wait point or network failure to be identified.
- Application code, database schema/data, API behavior and dependencies remain unchanged.


## Owner automated regression proof

- Corrected CR-01 static check: PASS.
- CR-02 popup static check: PASS.
- CR-03 active-data static check: PASS.
- Frontend production build: PASS; TypeScript completed and Vite transformed 71 modules in 2.64 seconds.
- Configured PostgreSQL/API regression: PASS.
- Authentication, missing JWT, duplicate email, wrong password and password-hash exclusion: PASS.
- Trial/active/free/expired/cancelled and inactive-user access rules: PASS.
- Admin users/subscriptions/catalog/history/feedback/full-access reads: PASS.
- Temporary commodity, market and Egusi/Kwali price CRUD/approval/outdated/cleanup: PASS.
- Feedback rating validation, submission, privacy, filtering, summary and cleanup: PASS.
- Final public active data remained Egusi and Kwali Market only: PASS.
- Final helper line: `CR-04 OWNER REGRESSION: PASS`.

The helper's fallback cleanup completed. No approved business record was removed.


## Owner browser/runtime verification

PASS. The final owner run showed:

- FastAPI/Uvicorn startup completed successfully.
- Public price requests returned `200 OK`.
- Registration returned `201 Created`.
- Valid login returned `200 OK`.
- The intentional invalid-login test returned `401 Unauthorized`.
- Profile and subscription reads returned `200 OK`.
- Public commodities, markets, and the Egusi/Kwali filtered price request returned `200 OK`.
- Protected admin all-record, user, subscription, price-history, and feedback-summary reads returned `200 OK`.
- Watchlist reads returned `200 OK`.
- No delete action appeared in this final browser verification.

The owner instructed continuation if the output was okay. These results satisfy the CR-04 gate, so CR-04 is owner-approved and CR-05 documentation is authorized.
