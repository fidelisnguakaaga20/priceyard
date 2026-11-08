# Access control

Every rule here is enforced on the server ([`app/utils/permissions.py`](../backend/app/utils/permissions.py)).
Hiding a button in the browser is never the protection.

## Roles and access levels

Two separate things decide what a person can do:

- **Role** (stored on the user): `free_user`, `paid_user`, `reporter` or `admin`.
- **Subscription** (one per user): `free`, `trial`, `active`, `expired` or `cancelled`.

**Full access** means an `active` subscription that hasn't passed its end date, a
`trial` that hasn't ended, or the `admin` role. A new account starts a 14-day trial.
The `reporter` role lets someone submit prices; it does not grant full access by
itself.

## What each level can do

| Feature | Guest | Signed in | Full access | Reporter | Admin |
|---|:-:|:-:|:-:|:-:|:-:|
| Current approved prices, commodities, markets, FAQ, testimonials, share cards | ✓ | ✓ | ✓ | ✓ | ✓ |
| Market signals | | ✓ | ✓ | ✓ | ✓ |
| Watchlist and alerts, feedback, flag a wrong price, referral link, checkout | | ✓ | ✓ | ✓ | ✓ |
| Price history, past-date prices and comparisons, older price records | | | ✓ | | ✓ |
| Quality signals, buying zones, sell-watch windows, storage suitability, cost breakdowns | | | ✓ | | ✓ |
| Submit a price for review | | | | ✓ | ✓ |
| Approve, edit or reject prices; manage the catalogue, intelligence, FAQ, users, subscriptions and payments; audit log; CSV export | | | | | ✓ |

A reporter with an active trial or paid plan also gets the "Full access" column.
Each endpoint's exact rule is listed in the [API reference](api-endpoints.md).

## Ownership

- Users can read only their own subscription, watchlist, push subscriptions and
  submission stats. Admins can read any subscription.
- Payment verification is tied to the signed-in user who started the payment.

## Protected owner account

The account matching the configured `OWNER_EMAIL` is protected
([`owner_policy.py`](../backend/app/services/owner_policy.py)):

- Only the owner can change the owner account, and it cannot be deactivated or
  demoted.
- Only the owner can manage other admin accounts or make someone an admin.
- The last active admin can never be deactivated or demoted.
- An admin whose access changed mid-session must sign in again before managing
  users.

## Private data

- A price's private source names are visible only to admins. They are never included
  in public price responses, CSV exports, audit responses or error messages.
- Feedback screenshots are visible only to admins.

## Machine-to-machine endpoints

| Endpoint | Protection |
|---|---|
| `POST /payments/webhook` | Paystack HMAC-SHA512 signature of the raw request body |
| `POST /subscriptions/cron/send-trial-reminders` | `X-Cron-Secret` header |
| `POST /internal/operations/recover-payments` | Short-lived GitHub OIDC token, accepted only from this repository's scheduled workflow on `master` |
