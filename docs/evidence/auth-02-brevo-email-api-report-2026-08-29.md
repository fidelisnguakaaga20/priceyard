# PriceYard AUTH-02 Evidence Report — 2026-08-29

## Outcome

Password-reset delivery now supports Brevo's HTTPS API for Render while retaining SMTP as a local fallback.

## Root cause

Render production logs showed `OSError: [Errno 101] Network is unreachable` while opening the Gmail SMTP connection. The failure occurred before SMTP authentication. Local Gmail SMTP delivery had already passed.

## Changes

- Added `BREVO_API_KEY` and `BREVO_API_URL` environment configuration.
- Email delivery prefers Brevo when its API key is configured.
- Requests use HTTPS, a 15-second timeout, and the API key only in the request header.
- Provider/network failures remain server-side and do not disclose account existence.
- SMTP remains the fallback when Brevo is not configured.

## Verification

- `python -m unittest discover -s tests -v`: 3 tests, PASS.
- `python -m compileall -q app`: PASS.
- Brevo request test verifies recipient, reset link, secret header, and absence of the API key from the JSON payload.
- Existing reset-token hash and single-use tests remain PASS.

## Production configuration

Set these on the Render backend service:

- `BREVO_API_KEY` — secret Brevo API key.
- `SMTP_FROM_EMAIL` — a sender verified in Brevo.
- `SMTP_FROM_NAME=PriceYard`.
- `FRONTEND_URL=https://priceyard.onrender.com`.

Existing SMTP variables may remain for local fallback. No secret is stored in Git.

## Scope confirmation

No database migration, frontend change, payment feature, prediction, marketplace, or other unapproved feature was added.
