# PriceYard progress — original appearance preserved

## Authority and baseline

2026-10-16: owner authorized progressive technical fixes, starting from restored
master 76dbd27588de4aa37f3163d8b263d4b72a2cff32. New branch:
codex/priceyard-original-preserved-20261016. Preserve backup branch
backup/priceyard-hardening-20261015 at 258991019e5af8b36eff407a8efa2c9fd03dd644;
use it only as reference, without merging its implementation wholesale.

Preserve original design, wording, fields, measurements, features and policies.
Trial stays 14 days; monthly NGN 2,500/30 days; seasonal NGN 6,000/90 days.
Keep original referral qualification/rewards and session policy unless separately
approved. No grade field, grade labels, guessed quantities or additional markets.
No production credentials, dotenv reads, production services/data, migrations,
push, merge or deployment. Local commits of verified batches are authorized.
Schema additions and visible/business changes require specific approval.

## Status and next step

Baseline browser/isolation verification passed. No application-source fix
has yet been applied. Next: batch 1, PY-15 price-refresh recovery, with unchanged
screens/wording. Apply small technical batches with automated and browser verification. Reuse
existing local tools from .git/priceyard-local-recovery-20261015; do not reinstall
or read private configuration. Runtime is tools/local-test/runtime (ignored).

## Checklist — do not repeat the audit

| ID | Improvement | Current status |
|---|---|---|
| PY-01 | Consistent historical access checks | Pending |
| PY-02 | Confidential/restricted market information | Pending |
| PY-03 | Google ownership and safe account linking | Pending; new linking UI requires approval |
| PY-04 | Password reset and login revocation | Pending; schema additions require approval |
| PY-05 | Referral abuse protection | Pending; preserve original rewards/qualification; policy changes require approval |
| PY-06 | Safe push notification destinations | Pending |
| PY-07 | Shared-device/session safety | Pending; preserve existing login duration |
| PY-08 | Input/upload/request abuse bounds | Pending |
| PY-09 | Concurrent security-action safety | Pending |
| PY-10 | Spreadsheet export safety | Pending |
| PY-11 | Correct saved administrator price state | Pending |
| PY-12 | Accurate existing quantity/type/market comparisons | Pending; no grades/new measurement fields |
| PY-13 | Consistent Nigerian dates/times | Pending |
| PY-14 | Evidence-based movement/confidence | Pending; wording/policy changes require approval |
| PY-15 | Prices recover after failed loading | Pending |
| PY-16 | Correct filters and response ordering | Pending |
| PY-17 | Correct market-detail loading | Pending |
| PY-18 | Accurate account/payment/access messages | Pending |
| PY-19 | Existing FAQ draft/hide/publish management | Pending |
| PY-20 | Bounded queries with accessible historical records | Pending |
| PY-21 | Reliable independent alerts | Pending; no new delivery promises |
| PY-22 | Efficient loading and accurate dashboard totals | Pending |
| PY-23 | Preserve layout while fixing mobile overflow | Pending |
| PY-24 | Keyboard/focus accessibility | Pending |
| PY-25 | Safe and clearly aged offline prices | Pending; visible additions require approval |
| PY-26 | Complete atomic administrative audit | Pending |
| PY-27 | Consistent existing editing/password inputs | Pending |
| PY-28 | Historical record preservation | Pending; no production migrations |
| PY-29 | Stable identities and dependent records | Pending; no automatic merge |
| PY-30 | Isolated automated/browser verification | Partial: baseline guards, 12 original tests, six real browser workflows passed; expand with each batch |
| PY-31 | Confirmed payment activation and recovery | Pending; schema additions require approval |
| PY-32 | Preserve unused purchased/trial time | Pending |
| PY-33 | Validate payment evidence | Pending |
| PY-34 | Expiry without unintended staff-role loss | Pending |
| PY-35 | Operational readiness and dependency evidence | Pending; production checks outside current scope |
| PY-36 | Accurate progress/documentation/maintainability | Progress record established; ongoing |

## Verified results and batch history

- Starting point: clean master at 76dbd27; backup tip verified unchanged before
  creating the new branch. No comprehensive audit repeated.
- Baseline synthetic database will use existing Egusi/Kwali Market and existing
  `1 bag` fixture, with bag_size left unknown. Fake prices/accounts clearly marked
  by the testing wrapper; no real customers or original database records copied.
- Baseline verified: six negative isolation checks passed (TCP/DNS, credential
  reads, native PostgreSQL, engine alternatives/persistent SQLite, child processes
  and nonlocal listeners; fresh memory DB and empty provider settings allowed).
- Original frontend TypeScript and Vite 5.4.11 build passed (99 modules, 2.01s).
  Original main bundle 315.10kB / 88.84kB gzip; CSS 31.58kB / 7.09kB gzip.
- All 12 original backend tests passed, zero failures/errors/skips, 14.892s.
- Six real-API Chromium browser workflows passed: original homepage/cards, real
  synthetic API/guest boundary/private-source exclusion, original price filters,
  Trial login/plans/history, Admin login/original price form, 375px mobile loading
  with no document overflow. No grade field/input/card label exists. Test harness
  selectors were corrected for existing labels/onboarding/Welcome heading; those
  were checker issues and no application changes were made to resolve them.
- Verified application source matches master before these checks. Fake seed has
  only Egusi and Kwali Market, unit `1 bag` copied from the existing test fixture,
  bag_size=NULL. Source authority: original migration 0006 and watchlist test.
- Browser link: http://127.0.0.1:55446. Fake logins free/trial/paid/reporter/admin
  @example.com, common password PriceYardDemo8!. Preview process ID stored in
  tools/local-test/runtime/preview.pid; server must be alive for link to work.
  Thin notice is testing wrapper only; original application source/CSS unchanged.
- Browser page requests allow only the literal test origin; service workers,
  native sharing/push and external links are disabled in this wrapper. This is
  focused UI/API evidence, not full PWA/provider/VM isolation certification.
