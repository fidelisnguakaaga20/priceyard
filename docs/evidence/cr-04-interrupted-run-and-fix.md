# CR-04 Interrupted Owner Run and Evidence-Helper Fix

Date: 2026-08-24

## Observed result

- CR-02 static check: PASS.
- CR-03 static check: PASS.
- Frontend TypeScript/Vite production build: PASS; 71 modules transformed.
- CR-01 static check: FAIL only because Login/Register did not contain the literal word `finally`.
- CR-04 configured regression: owner interrupted after more than 20 minutes with no output after the password prompt.

## Cause assessment

The Login/Register handlers use two explicit `setBusy(false)` paths so loading clears before success/error popups, which is the approved CR-02 sequence. The old CR-01 checker was stale; the working product and production build were not defective.

The original CR-04 helper accumulated results silently until the end and inherited an unbounded PostgreSQL connection attempt, so a transient Supabase/DNS/pooler wait could not be located promptly.

## Smallest fix

- Evidence checker only: require two explicit Login/Register `setBusy(false)` calls instead of requiring `finally`.
- Evidence helper only: print every phase/PASS with flushing.
- Evidence helper only: add a 15-second PostgreSQL connection timeout without changing application configuration.

## Scope

No frontend component, backend route/service, API contract, database schema/data, dependency, subscription/access rule, disclaimer or approved feature changed. CR-04 remains IN PROGRESS pending retest.
