# Local Admin list paging — approved2026-10-18

Your instruction requires approval for new visible product features. This
proposal adds visible navigation controls; it is not covered by routine local
command/test approval. Owner explicitly answered "Approve Admin list paging" on
2026-10-18. The following local scope is authorized; production remains excluded.

Current behavior: Admin lists download and render every matching record. As
history grows, this can consume large amounts of browser/server memory. Prior
query/CSV/dashboard fixes do not bound these full JSON lists.

Proposed scope:

- Display at most100 records per page in the existing Admin record lists: Users,
  Subscriptions, Payments, Prices/flagged records, Audit logs, Feedback, Commodities,
  Markets, FAQs and the six existing intelligence lists.
- Add only Previous/Next controls and page information, using existing button
  styles. Preserve existing headings, columns, cards, forms, terminology, filters
  and existing actions. Do not add a search box, other fields or a new screen.
- All records remain reachable; never silently truncate or delete rows. Existing
  totals and all14 dashboard cards count the complete matching database records,
  rather than counting the current page. Keep original ordering with an ID tie
  breaker. Editing/reloading retains the appropriate filter/page where possible;
  a now-empty last page moves back safely.
- Existing ID-based edit forms must still load records beyond the current page.
  Authorization, source redaction and atomic audit rules remain unchanged.
- Bound database/serialization/client batches. Preserve existing full-list API
  callers through a bounded streaming compatibility path, or return for further
  approval if a compatible implementation cannot preserve their results. Do not
  silently change an old API request into a partial list.
- No database fields, migrations, pricing/referral/session changes, dependencies,
  production services/data, push/merge or deployment. Local implementation and
  synthetic backend/PostgreSQL/browser tests only, in small batches.

Acceptance: test records across page boundaries/ties; all IDs remain reachable;
authorization and filtered totals remain accurate; edit/reload/delete behavior
is safe; original14-card counts and unchanged layout work on mobile/desktop;
database and browser materialization stays bounded per page. Use a few hundred
small synthetic rows, not large repeated fixtures or overlapping test processes.

This approval would cover Admin lists only. Public price/history/chart behavior
is preserved and remains separate PY-20 work; no approval to truncate charts or
price history is requested here. API implementation details must be verified
before changing callers.

Decision: APPROVED by owner2026-10-18; implement/test/commit locally in small batches.

Verified through batch71:8/16 lists (Users/Payments67, Commodities/Markets68,
FAQs/Audit70, Market/Quality signals71). Signal editors preserve off-page ID
loading through existing detail endpoints, cancel obsolete requests and reject
mismatched IDs; old full/scoped streams and access rules stay intact.
FAQ pages keep the original visible published-first/hidden-second
group ordering, then category/ID within groups; legacy full FAQ arrays retain
their original category/ID order. Known-ID editing/publication works beyond the
current page. Public FAQ arrays remain complete and published-only. Audit pages
and full streams apply the existing response-time redaction, retaining raw
historical evidence. No subscription expiry or other listing rules changed.
