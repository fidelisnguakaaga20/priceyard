# CR-03 Active MVP Data Reset — Build Report

Date: 2026-08-24

## Result

Implementation and automated verification: PASS.

Real PostgreSQL migration, runtime smoke, and owner browser verification: REQUIRED before CR-03 final approval and CR-04 authorization.

## Audit findings

- `commodities.is_active` and `markets.is_active` already exist; no new column is needed.
- Commodity and market create/update schemas and admin CRUD already support `is_active`.
- Price creation already rejects inactive commodity/market references.
- No production seed module exists. Earlier test helpers referenced the previous four-market/three-commodity set but are evidence utilities, not runtime seeding.
- Public catalog and approved-price queries did not consistently exclude inactive references.
- Admin frontend reused public catalog/history endpoints, so protected all-record endpoints are required to preserve completed management work.

## Implementation

- Alembic data revision `0006_cr03_egusi_kwali` ensures Egusi and Kwali Market exist, deactivates every other commodity/market, and activates one canonical target record of each type.
- No record or table is deleted. Users, subscriptions, auth data, audit logs, price records, and relationships are untouched.
- Public commodity/market lists and direct catalog views are active-only.
- Public current/detail/history/comparison price queries require both active commodity and active market.
- New admin-only all-record catalog/history endpoints preserve inactive-record visibility and reactivation/CRUD.
- Prices page commodity and market filters load active API catalogs as selects.
- Admin catalog/dashboard/price pages use protected all-record endpoints where required.

## API changes

- Changed public behavior: `GET /commodities`, `GET /markets`, public catalog detail, and public price retrieval now exclude inactive references.
- Added protected admin endpoints: `GET /commodities/admin/all`, `GET /markets/admin/all`, and `GET /price-updates/admin/history`.
- Existing POST/PATCH/DELETE APIs and access/subscription rules remain intact.

## Automated proof

- Python compilation: PASS.
- Focused CR-03 static scope/query/migration check: PASS.
- TypeScript compilation: PASS.
- Vite production build: PASS.

## Outstanding gate

The migration has not yet been applied to the owner's configured PostgreSQL database. The owner must run `cr-03-owner-verification-steps.md` and provide the real migration, database, API, CRUD, access-control, and browser proof.

## Scope confirmation

No CR-04 regression stage, table deletion, user/auth/subscription/audit mutation, payment, marketplace, AI feature, dependency, or theme redesign was included.

