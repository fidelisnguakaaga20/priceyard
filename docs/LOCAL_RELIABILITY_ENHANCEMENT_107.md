# Local watchlist reliability and account privacy

The watchlist could apply an older network response after a newer save/removal.
The original compiled build reproduced three failures: a deleted item reappeared,
an obsolete error replaced a successful result, and a previous account's completed
save triggered a late refresh after its view was disposed.

Superseded reads now cancel and check request generation/account identity before
applying rows, errors or loading state. Account-specific rows and unfinished
targets clear before another account is painted. Completed mutations cannot
refresh, change controls or show messages for a superseded account. The existing
saved-price provenance helper forwards an optional AbortSignal without changing
its defaults, authentication, caching or timestamp checks.

Original JSX, CSS, labels, fields, prices, measurements, subscription rules and
all14 Admin cards stay unchanged. No backend/database/dependency change.

| Executed verification | Result |
| --- | --- |
| Existing watchlist API validation/storage/ownership |2 tests pass |
| Original compiled build |3 expected browser failures reproduced |
| Fixed browser: save/reload/remove, stale success/error, account switch |8 checks pass |
| Shared API: provenance, invalid cache times, auth errors, cancellation |14 checks pass |
| TypeScript and Vite production-style isolated build |Pass; installed snapshot reused |
| Admin dashboard |All14 labels/totals correct; one summary request; outage recovery passes |
| Independent code review and whitespace checks |Pass |

The race tests also ignore cancellation deliberately, proving obsolete replies
are rejected even when transport completes. All actual HTTP occurs inside the
guarded loopback browser; the test harness's initially blocked Node-side request
method was replaced without weakening network restrictions. Its account switch
now follows the existing logout/login flow. No unresolved final test failure.

Only synthetic accounts/data were used. No external browser request or page error.
No PostgreSQL rerun was necessary for a frontend-only batch. Tests ran sequentially
with one browser, no new dependency tree or cloud infrastructure. The synthetic
preview remains at http://127.0.0.1:55446/watchlist; use free@example.com with the
existing fabricated demo password shown by the preview.

Evidence: `tools/local-test/runtime/enhancement-107-summary.json`,
`watchlist-race-before.json`, `watchlist-race-after.json`, `offline-api-checks.json`
and `dashboard-checks.json`. Synthetic rows created by successful tests were
removed and their previous watchlists compared unchanged.

**35/36 remain complete.** PY-35's actual backup/restore, hosted/provider and other
live gates remain open. The production credential-window rejection was not
retried or bypassed. No production access, real backup, customer record change,
migration, push, merge or deployment occurred.
