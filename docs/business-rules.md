# Business rules

The product rules the code enforces, and the reasons behind them.

## Prices

- **Ranges, not single numbers.** Market prices vary from trader to trader, so a
  price is recorded as a low–high range. An optional average must fall inside it.
- **Nothing is invented.** A missing unit, bag size or type stays "not recorded".
  Records are never given a measurement copied from another record.
- **Like with like.** Charts and comparisons connect only records with the same
  market, unit, bag size and type. Different series are shown separately.
- **Review before publishing.** Reporter submissions are pending until an admin
  approves them. Members can flag a price that looks wrong, and admins see flagged
  prices in their own list.
- **Evidence for claims.** "Verified by 2 sources" requires two distinct private
  source references. A reporter's up/down/stable movement must be supported by the
  previous approved record with matching specifications; otherwise it is "unknown".
- **Sources stay private.** Source names are visible only to admins.
- **Nigeria time.** Price days and times are entered and shown in WAT. Billing
  dates use UTC.
- **History is preserved.** Old records are kept. A record can be marked outdated
  rather than rewritten.

## Access and plans

| Plan | Price | Length |
|---|---|---|
| Trial | free | 14 days from registration |
| Monthly | ₦2,500 | 30 days |
| Seasonal | ₦6,000 | 90 days |

- Renewing adds the new days after any remaining paid time. Buying during a trial
  keeps the remaining trial days, and the paid days start after them.
- Access is granted only after Paystack confirms the payment: the amount, currency
  and reference must match.
- An account given open-ended access by an admin cannot start a new checkout, so a
  manual grant is never overwritten.
- Without full access, users still see current approved prices, commodities,
  markets and the FAQ. History and deeper market intelligence need full access
  ([access control](access-control.md)).

## Referrals

- Each user has a referral code. When a new person registers with it, the referrer
  gets 7 extra trial days while they are on free access or an active trial.
- At most 3 bonuses per referrer in any rolling 30 days. Every referral still counts,
  and the new person still gets their own 14-day trial.

## Offline use

The installed app can show the last saved public prices without a connection. They
are always labelled as a saved copy, with the time they were saved on the device.
Private, history and signed-in data is never saved for offline use.
