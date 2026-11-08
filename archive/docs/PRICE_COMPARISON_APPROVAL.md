# Approved price-comparison safeguard — local implementation authorized

Scope: PY-12 and the existing Price History / commodity-detail charts only, in
isolated local testing. Owner explicitly approved on 2026-10-17:
"Approve the comparison safeguard". Implementation and verification follow in
small batches; this is not production authorization.

Current code feeds all selected historical records into one trend line. A change
of market, number of bags, bag size or commodity type can look like a price rise
or fall even though the records describe different purchases. Existing current
selection also chooses one record per commodity/market without separating quantity.

Recommended rule:

- Keep every historical record, existing price, label and measurement unchanged.
- A continuous trend or calculated price difference must use the same commodity,
  market, number-of-bags text, bag-size text and existing commodity-type text.
  Compare text after trimming and case folding only; no conversion or guessing.
- Different markets can be compared side by side only when their recorded
  quantity/type fields match. They must not form one continuous time series.
- Missing bag size/type means unknown, not proof of equal specifications. Keep
  such records visible, but do not calculate a supposedly comparable difference
  or join unknown-size records into a trend without an owner-approved equivalence.
- Use existing recorded measurements to label separate chart groups. If evidence
  is insufficient, use a short "Not enough comparable records" message instead
  of a misleading connected line. Keep the history table/cards and all rows.
- Show the latest current record for each existing distinct recorded quantity/type
  combination rather than silently replacing an unlike quantity with another.
  This may increase current cards for a commodity/market that has multiple sizes.
- Leave recorded movement, previous-price fields, confidence, market-day rules,
  freshness thresholds, subscriptions and existing history intact. Their business
  interpretation is a separate decision. No grades, new markets, new measurement
  fields, data backfill, automatic renaming/merging or production changes.

Owner review points: separate visible chart groups, insufficient-evidence wording
and potentially additional current cards are visible changes. This approval does
not change the fourteen Admin dashboard card types; Latest updates would count
the resulting current records using the same shared selection query.

Acceptance: synthetic tests prove unlike quantities/markets are never joined,
all stored/history rows remain, matching records retain their existing prices,
and no missing quantity is fabricated. Backend, PostgreSQL and original-browser
verification must pass before a local implementation commit.
