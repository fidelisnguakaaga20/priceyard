# Approved local-only offline-price safeguard

Owner explicitly replied “Approve the offline-price safeguard” on 2026-10-17.
This approval covers the local-only scope below; no deployment or production work.

The original service worker can replay previously cached public responses without
telling the page that the network failed or when this device saved that copy.
The existing offline banner depends on the browser's online indicator, which does
not prove that a request to the application server succeeded. This is a source-level
risk to be reproduced under isolated tests, not evidence of a production incident.

Requested visible changes, using the existing banner styling:

- Offline banner: “You're offline. Saved prices may be shown; they are not live.”
- When a price request actually falls back to a saved copy, identify it beside its
  price section: “Saved copy — not a live price. Saved on this device: {date/time}.”
  Keep each record's existing update time visible; saving a copy never makes its
  underlying market observation newer. Distinguish device save time from record time.
- Do not invent a timestamp for an old unmarked cache entry. Fetch it successfully
  again before treating it as a usable saved copy. A device offline before that
  refresh may have to reconnect before it can show prices.

Technical boundaries within that approval:

- Cache only recognized public current-price/catalog/FAQ resources from the
  application's configured API location, and the application's own shell/assets.
  Do not assume production frontend and backend share an origin.
- Never cache or replay authenticated requests, historical/date-selected price
  requests, account/Admin/payment/reset endpoints or responses with errors.
- Retain offline public-price functionality with truthful provenance; no automatic
  new expiry interval, forced price-age cutoff, new paid-access rule or guessed
  meaning/confidence. Old unmanaged PriceYard cache copies may be discarded only
  from the local test browser during testing. Production browser rollout remains
  unapproved along with deployment.
- Verify the actual service-worker source under a fake isolated origin/cache and
  the real original interface with synthetic responses. Keep production/provider
  network and credentials blocked, including while simulating an outage.
- No database fields, migrations, saved price edits, layout redesign, provider
  access or production modification. This document does not itself grant approval.

Owner decision: **APPROVED**. Implementation/test results belong in the progress log.
