# PY-14 new price claims - owner decision required

Current Admin forms let an editor choose movement/confidence labels. Reporter
submissions already cannot self-assign editorial verification. Existing labels
and source privacy must stay; names in source fields do not prove a real-world
check occurred. Stored history must not be rewritten to invent missing evidence.

Recommended local-only rules for new/changed claims and new approval:
- Keep original labels/forms/measurements. A new/changed "Verified by 2 sources"
  claim requires two nonempty, different references in the existing private
  source fields. This records the editor's evidence; it does not independently
  authenticate the people. "Admin confirmed" and "Market visit confirmed" stay
  deliberate Admin assertions, not automatically inferred confidence.
- A newly asserted up/down/stable movement requires an earlier approved,
  non-outdated record of the same commodity, market and complete recorded
  measurements/type, using the existing approved comparability rules. Select the
  most recent such preceding record; do not guess missing sizes or conversions.
- Up means both range endpoints increased; down means both decreased; stable
  means both are unchanged. Mixed/crossing endpoints or insufficient comparable
  evidence support only the existing "unknown" option. An editor may always
  choose unknown rather than claim more certainty.
- Reject an unsupported new claim with an explanation instead of silently
  replacing the editor's value. Original guidance/price values stay untouched.
  If previous range values are supplied with a movement claim, they must agree
  with that supporting record; missing values are never filled by guessing.
  Review the claim before approving an old pending record for new publication.
- Ordinary corrections that do not alter a claim or its supporting inputs do
  not relabel old history. Historical unsupported published claims require a
  separately authorized editorial review under PY-35; no bulk rewrite/delete.
- No grade system, new fields, mandatory guessed measurements, price-age cutoff,
  automatic trading advice, access changes, production data or migrations.
  Test both endpoint directions, overlap/equality/missing inputs, same identity/
  measurement/time boundaries, source privacy and original moderation workflows.

Tradeoff: editors may have to use "unknown" until comparable observations are
recorded, even if they have other informal knowledge. This is a stricter
publication policy, so it needs the owner's approval before implementation.
Real-world source independence/market accuracy still require human verification.

Decision: owner answered "Approve evidence safeguards" on2026-10-18.
Implement/test this scope locally; historical production editorial review and
real-world source verification remain outside authorization under PY-35.
