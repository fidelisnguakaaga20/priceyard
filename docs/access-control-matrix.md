# PriceYard access-control matrix

Current hardening-branch contract, October 2026. Backend authorization is authoritative.
Earlier stage pre-fix matrices are superseded by the full development authorization.

Commercial entitlement and work authority are independent. Free/expired accounts
receive limited access. Valid Trial/Paid/manual grants provide full commercial
access. Reporter/Admin authority does not disappear when a subscription expires.

| Capability | Guest | Free / expired | Valid Trial | Valid Paid / manual grant | Reporter | Admin |
|---|---|---|---|---|---|---|
| Active public catalogs, published FAQ/testimonials | Yes | Yes | Yes | Yes | Yes | Yes |
| Current public price summaries | Yes | Yes | Yes | Yes | Yes | Yes |
| Complete eligible history and dated searches | No | No | Yes | Yes | With full entitlement | Yes |
| Basic market-signal facts | No | Yes | Yes | Yes | Yes | Yes |
| Deeper signal/quality/buying/sell/storage/cost intelligence | No | No | Yes | Yes | With full entitlement | Yes |
| Own watchlist, preferences, feedback, subscription/payment status | No | Own | Own | Own | Own | Authorized management too |
| Submit pending price and own statistics | No | No | No | No | Yes | Yes |
| Approve/reject/correct/withdraw prices | No | No | No | No | No | Yes |
| Master data, user, subscription, payment, FAQ, audit/export administration | No | No | No | No | No | Yes |
| Private market source identities | No | No | No | No | No editorial-source access | Authorized management only |

Disabled accounts cannot perform authenticated actions. Their bearer credentials
are revoked; reactivation does not resurrect them. Public pages remain accessible
anonymously. An invalid supplied Authorization header is rejected rather than
silently treated as Guest.

## Field boundaries

Public current summaries preserve ranges, previous ranges, optional recorded average,
measurement/grade, movement, confidence and observation time. They omit
possible_meaning, suggested_action and notes. Full consumer responses add these
premium fields. They still exclude private source_1/source_2 and administrative
contributor fields.

Basic market signals omit deeper meaning/action. Quality and the other intelligence
families require full access for list and detail. Source identities remain absent
from consumer responses, notifications, general audit snapshots and CSV exports.

Reporter POST accepts a raw pending observation and strips source/editorial claims.
A Reporter cannot approve, access unrelated management APIs, or bypass commercial
gates. Explicit staff access grants are commercial records, not automatic Reporter
privileges.

## Historical access and preservation

- Date parameters on current/comparison paths require full access.
- Limited direct-ID reads allow only eligible current series records.
- Consumer history requires approved records and active commodity/market references.
- Outdated approved observations remain in eligible history.
- Current selection never falls back beneath an outdated latest record.
- Admin history retains inactive/status visibility.
- Withdrawal/archive preserves business evidence instead of physical deletion.
- Personal resources require their account owner, or an explicitly authorized Admin.

Cancellation of future access intent does not remove valid purchased/manual access.
At the actual cutoff, commercial access becomes limited while staff authority stays.

## Proof and remaining limits

Synthetic service/API tests verify forbidden status codes and absence of premium
fields, not only frontend hiding. Real main-ASGI tests use genuine synthetic JWT
sessions and transaction middleware. See
[price evidence](evidence/backend-price-hardening.md) and the
[current progress record](../PRICEYARD_PROGRESS.md).

These tests do not inspect live account entitlements. Refresh credentials remain
JavaScript-readable; HttpOnly cookies and administrator MFA are not implemented.
No public sample quota or paid-plan price change was introduced.
