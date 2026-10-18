# PY-05 referral decision - approved local scope

The current rule awards seven extra trial days when a referred person registers,
for an eligible free/live-trial referrer. Paid, expired and cancelled access keeps
its existing treatment. Registration/reward/audit already save atomically;
duplicate registrations cannot award twice. Identity verification is not required
for the reward, and there is currently no limit on awards. Multiple fabricated
registrations can therefore extend a trial repeatedly.

Recommended local-only choice for owner consideration: at most three newly
awarded referral bonuses per referrer in a rolling30-day UTC period. Each bonus
stays seven days, earned at registration under the same eligibility rules.
The suggested number is a business recommendation, not an existing approved rule.
It keeps a useful invitation benefit while limiting automatic free-access growth.

Exact proposed boundaries:
- Preserve all already-earned days, purchased time, existing referral links/counts
  and the original14-day trial. Never take away a historical bonus.
- Further referred people can still register and receive their own14-day trial;
  registration must not fail just because the referrer reached the award limit.
- Count only known successful reward audit events in the previous30 elapsed days;
  an event exactly30 days old falls outside the window. Recheck under the existing
  parent-account lock so simultaneous registrations cannot exceed the cap.
- Update only the existing referral explanation to state the limit and existing
  free/live-trial eligibility truthfully. No new fields, screens or verification
  requirements. No IP-based identity assumptions on shared Nigerian networks.
- Do not guess unknown legacy award history, edit old audits or remove time.
  Any production legacy review is separate PY-35 work and remains unauthorized.
- Test boundaries, concurrent last-slot registration, duplicate/failed signup,
  paid/trial preservation and original referral dashboard behavior synthetically.

Tradeoff: some genuine referrers would earn fewer automatic bonuses. This cap
does not prove that accounts belong to distinct people or eliminate all fraud.
Keeping the current policy is also an owner choice, with that abuse risk retained.
Changing qualification to verified email, first payment or manual review would
need a separate decision; none is proposed for automatic implementation here.

Decision: owner answered "do the best option" on2026-10-18 to the explicit
three-bonus rolling30-day proposal. Implement this recommended scope locally;
preserve existing bonuses, eligibility and purchased time. No production scope.
