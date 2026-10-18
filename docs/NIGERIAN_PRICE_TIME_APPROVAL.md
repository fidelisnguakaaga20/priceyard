# PY-13 — proposed Nigeria price-time rule; awaiting approval

Your instructions require specific approval for business rules and visible
changes. This proposal changes the meaning of a price's selected calendar day
and adds a time-zone label. No implementation is authorized by this document.

Current behavior: price displays use the viewer's device time zone, and dated
price queries use UTC midnight boundaries. Existing Admin/Reporter inputs
correctly convert the device's local time to stored UTC. These can describe
different calendar days around midnight or for someone outside Nigeria.

Recommended local-only rule:

- Use Nigeria market time, WAT (UTC+1), consistently for agricultural price
  timestamp displays, price-entry/correction wall-clock inputs and dated price
  queries/comparisons/CSV filters. Label existing price-time inputs/display
  context "Nigeria time (WAT)"; keep the same controls, fields, layout and terms.
- Example:00:30 WAT on18 October is stored as23:30 UTC on17 October, and belongs
  to the18 October Nigerian price day. Query intervals are inclusive start and
  exclusive next midnight. Ordering, quantities and comparison groups stay.
- Continue storing UTC instants; do not rewrite historical rows, guess missing
  timestamps or infer what an ambiguous legacy wall-clock value originally meant.
  Any genuinely ambiguous production records require separate manual review.
- Keep current-record/history entitlement unchanged. Preserve the14-day trial,
  NGN2,500/30-day and NGN6,000/90-day plans, paid whole-day UTC expiry and approved
  purchased-time preservation. Do not change billing/account time rules.
- No new database/form fields, migrations, dependencies, production access or
  deployment. Test midnight boundaries in backend/PostgreSQL and the browser
  running in Lagos and UTC; compare unchanged raw stored timestamps/history.

Alternative: retain current device-local display/input and UTC date filters,
leaving the PY-13 business-time decision pending. The recommended rule is more
consistent for a Nigerian market-information service and changes times shown
to users outside Nigeria; it is a business choice, not merely a code cleanup.

Decision: APPROVE / MODIFY / REJECT: __________________
