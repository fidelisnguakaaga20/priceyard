# Cost reference quantity — owner decision required

Current cost records store commodity, market and monetary amounts, but no unit,
bag size or linked price record. CommodityDetailPage currently labels a cost
reference using the first current price's bag size/unit for that market. That
relationship does not prove which quantity the saved costs describe.

Proposed local-only correction, independent of the approved chart safeguard:

- Keep all cost amounts, rows, formulas, fields and the existing calculator.
- Stop inferring its unit from an unrelated current price, even when only one
  current price exists. Do not guess a bag weight or silently convert costs.
- Replace the unsupported per-weight label with "Unit not recorded" and show:
  "Confirm the unit for this cost reference before using this estimate."
- Continue multiplying entered quantity by the saved reference amounts; describe
  them as reference units rather than a verified bag size. No new unit field,
  historical backfill, migration, paid-access change or production operation.

Acceptance: unlike current-price variants cannot relabel saved cost figures;
original totals/quantity calculation remain unchanged; the uncertainty message
appears in the original calculator area and no new measurement is invented.

Status: awaiting explicit owner approval for this visible wording/label change.
