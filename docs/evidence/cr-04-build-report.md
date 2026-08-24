# CR-04 Regression Testing — Build Report

Date: 2026-08-24

## Current result

Regression helper implementation and syntax verification: PASS.

Owner production build, configured PostgreSQL/API regression and read-only browser verification: REQUIRED before final CR-04 approval.

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
