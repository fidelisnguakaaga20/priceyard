# Google account linking: owner decision

Status: owner approved using the proposed secure, practical option on 2026-10-16:
"do the best that is user firendly and same time secured for the app".
Implementation and verification are still pending at this checkpoint.

Current original behavior: after Google token verification, the service looks up
the Google subject. If not found, it matches email and attaches that subject to
the existing account, potentially replacing its existing google_id. No separate
proof of the existing PriceYard login is required.

Proposed local-only rule, requiring owner approval because existing sign-in
behavior changes:

- Existing accounts already linked to the verified Google subject keep signing in.
- An unmatched Google subject must not attach to or replace an existing account
  solely because its email matches. Return a controlled error asking the person
  to use their existing PriceYard login. Preserve the existing account, password,
  Google binding, role, subscription, payments, referral and history records.
- A genuinely new Google email/subject can still create the original account with
  the existing 14-day trial. No new pricing, reward qualification or account fields.
- No new linking screen, recovery mechanism, historical unlink/backfill, automatic
  account merge or production operation. A future password-confirmed linking flow
  needs separate approval before implementation.

Compatibility: people who previously used only a PriceYard password and now try
Google with that email will need to continue with their password (or the existing
password-reset flow). Existing Google-bound users and ordinary password sign-in
remain supported. Existing mistaken legacy bindings cannot be identified safely
from local synthetic data and will not be changed automatically.

Verification after approval: synthetic HTTP/SQLite and marked PostgreSQL tests
must prove subject ownership, same-email non-linking/no overwrite, unchanged
trial/access/history/password behavior, inactive-account denial, concurrent signup
conflicts and clean rollback. Browser requests use fabricated Google verification
responses only; no real Google token, credential, account or provider contact.

Independent technical work, already authorized: validate verified claims strictly,
bound token inputs and provider request duration, and handle verification outages
without creating users or reporting uncontrolled server errors. These do not
authorize changing the email-based linking rule before approval.

Read-only contract reference: https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
(2026-10-16). Google identifies users by stable subject and recommends an existing
password challenge for account linking, particularly for third-party email domains.
