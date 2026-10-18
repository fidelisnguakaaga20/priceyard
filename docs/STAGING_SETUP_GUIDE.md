# PriceYard staging setup — owner checklist

Staging is a separate practice copy. It must contain only invented accounts,
prices and transactions. Your current live PriceYard stays unchanged. Nothing
below has been purchased, deployed or configured in an external account.

## What to provide

| Item | What is needed |
| --- | --- |
| Website address | One dedicated staging hostname and its full HTTPS address. Also list any other live PriceYard hostname aliases so they can be excluded. Do not reuse the live hostname |
| HTTPS hosting | An existing separate hosting project/service name, approved operator and secure configuration location. Valid HTTPS certificate, supported runtime and frontend/backend on the same site; preferably API under `/api`. No automatic production deployment or background jobs |
| Test database and app secret | A separate empty PostgreSQL database with staging-only credentials (`DATABASE_URL`), plus a new staging-only `JWT_SECRET`. No production Supabase connection, customer export or reused production secret |
| Paystack TEST | Dedicated approved TEST setup, `PAYSTACK_PUBLIC_KEY` (`pk_test_…`) and `PAYSTACK_SECRET_KEY` (`sk_test_…`). No live keys, real cards or real payments |
| Google sign-in | Separate approved web OAuth client/project, client ID, exact staging JavaScript origin and named Google test accounts. Set `GOOGLE_CLIENT_ID` and frontend `VITE_GOOGLE_CLIENT_ID` to the same test client ID. Current app uses Google Identity Services popup/callback; it does not require a client secret or an invented server callback route |
| Reset/notification email | Approved test sender and either a dedicated `BREVO_API_KEY`, or `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` and TLS/SSL selection. Both methods need `SMTP_FROM_EMAIL`; sender name uses `SMTP_FROM_NAME`. Approve exact receiving email addresses; do not assume a provider automatically blocks customer delivery |
| Push / WhatsApp, if being tested | Staging-only `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_CLAIM_EMAIL`; frontend `VITE_VAPID_PUBLIC_KEY`. For WhatsApp:approved test sender/phone-number ID and access token (`WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`), approved API version and exact allowed test phone numbers. Leave unavailable channels disabled |
| People/devices and alerts | Written list of consenting test email addresses, Google accounts, phone numbers and browser devices; one approved monitoring-alert recipient and operator. Never provide anyone's account password |

## Simple steps

1. **Choose the practice address.** Give your hosting operator the name you want
   for the separate staging site. Ask them to confirm its HTTPS address and that
   its hosting/database are separate from live PriceYard. Do not buy anything or
   change an existing live service for this step. If no suitable resource exists,
   record that it is unavailable for a separate decision.
2. **Choose your testers.** Write down exactly which email addresses and phone
   numbers may receive test messages, and which phones/browsers will be checked.
   Use accounts controlled by you or consenting testers, never customer lists.
3. **Have the operator prepare test connections.** Ask them to use Paystack TEST
   credentials, a separate Google test client and dedicated message credentials.
   Any new provider setting or sender change needs your approval first; leave
   existing live provider settings alone.
4. **Store secrets privately.** The operator enters keys/passwords into the staging
   host's protected settings/secret store. Do not paste them into this chat, email,
   screenshots or Git. Share only the project name, staging URL, secure storage
   reference and non-secret list of approved testers.
5. **Check the address settings before startup.** Operator sets `APP_ENV=staging`,
   `FRONTEND_URL` to the exact HTTPS staging origin (no page path/query), and
   `CORS_ORIGINS` to that same origin. Set frontend `VITE_API_URL=/api` for the
   same-site arrangement. Explicit `FRONTEND_URL` is mandatory for notifications;
   missing/invalid settings skip alerts rather than guessing a live URL.
6. **Review provider destinations before any test.** In the recommended `/api`
   arrangement, payment return is `<staging-origin>/payment/callback` and webhook
   is `<staging-origin>/api/payments/webhook`. Google allowed JavaScript origin
   is the exact staging origin. These are operator-reviewed settings, not commands
   run by this guide. Keep the scheduler and external messaging disabled until
   database identity, test-key mode, host restrictions and recipient limits are
   checked. The current app does not supply a global provider-recipient allowlist;
   a restricted test harness/provider sandbox must enforce it before real sends.
7. **Use the practice site only after readiness is confirmed.** Operator first
   verifies the synthetic database and original screens. Then test login/reset,
   test-only payment, approved message receipt and all14 Admin cards one workflow
   at a time. Do not use a real card, customer account or live website as fallback.

The notification URL guard rejects the original known production host outside
production mode. Additional live aliases must be reviewed before staging sends.
With `APP_ENV=production` and the original live `FRONTEND_URL` explicitly set,
the production email destination is unchanged. Existing production configuration
has not been inspected; compatibility depends on configuring that value correctly
before a separately approved future release.

## Understanding the results

- **Passed:** the named check ran and met its acceptance criteria.
- **Failed:** the check ran and its result was wrong; retain its failure evidence.
- **Blocked:** a required host, credential, recipient approval or tool is missing;
  the external check was not attempted. This is not a proven application failure.
- **Not attempted / Awaiting Production Approval:** outside this staging scope,
  including production databases, real customer backups and deployment.

Current details:[Phase 1 report](PY35_PHASE1_REPORT.md). No production permission
or credential request is made by this guide.
