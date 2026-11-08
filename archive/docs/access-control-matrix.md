# PriceYard Stage 20 Access-Control Matrix

Status: **IN PROGRESS — pre-fix assessment**

Authority: PriceYard Official Reference Document → Architecture Design → AI Project Execution Plan.

The backend is the security authority. Frontend hiding is presentation only and is never accepted as access-control proof.

| Access state | Public/sample prices | Published FAQ | Feedback submit | Watchlist | Basic market signals | Quality/deeper intelligence | Buying zones | Sell-watch | Storage suitability | Cost breakdown | Admin APIs | Expected Stage 20 result | Current assessment |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Guest | Yes, limited/sample only | Yes | No | No | No | No | No | No | No | No | No | Public/sample only | **FAIL — public price response currently includes deeper guidance fields (`possible_meaning`, `suggested_action`, notes/extra detail) beyond the approved public Prices-page field set.** |
| Free | Yes, limited | Yes | Yes | Yes | Yes, basic only | No | No | No | No | No | No | Limited + feedback/basic watchlist | **FAIL — market-signal API currently returns full signal meaning/action and quality-signal API is available to any authenticated active user.** |
| Trial | Yes, full approved access for 14 days | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Full approved user access | PASS by existing subscription/full-access guards, pending owner runtime matrix test. |
| Active Paid | Yes, full approved access | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Full approved user access | PASS by existing subscription/full-access guards, pending owner runtime matrix test. |
| Expired | Yes, limited | Yes | Yes | Yes | Yes, basic only | No | No | No | No | No | No | Same limited access as Free | **FAIL for same Free-tier signal/quality exposure gap; premium Stage 10–12 endpoints are already blocked.** |
| Cancelled | Yes, limited | Yes | Yes | Yes | Yes, basic only | No | No | No | No | No | No | Same limited access as Free | **FAIL for same Free-tier signal/quality exposure gap; premium Stage 10–12 endpoints are already blocked.** |
| Inactive | Public pages only; authenticated account access blocked | Published FAQ | No authenticated action | No | No | No | No | No | No | No | No | Account is blocked by backend | PASS by `get_current_user`/login active checks, pending owner runtime test. |
| Admin | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Full administration | PASS by role guards, pending owner runtime matrix test. |

## Stage 20 protected-endpoint expectations

The following existing backend endpoints are treated as full-intelligence endpoints and must return 401/403 to Guest/Free/Expired/Cancelled/Inactive as applicable, while Trial/Active Paid/Admin may read them:

- `GET /quality-signals`
- `GET /buying-zones`
- `GET /sell-watch-windows`
- `GET /storage-suitability`
- `GET /cost-breakdowns`

`GET /market-signals` must provide only the approved **basic** signal view to limited authenticated users; deeper meaning/action belongs to full approved intelligence.

Public price endpoints must not expose private source identities or deeper premium guidance to Guest/limited users. Admin responses may contain private-source/admin fields only under admin authorization.

## Current pre-fix finding

Stage 20 cannot pass without an approved access-control correction. No production/backend/frontend behavior has been changed by this assessment. The required correction is subject to the project Change Control rule before implementation.
