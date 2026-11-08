# CR-03 Owner Verification

Date: 2026-08-24

## Result

RETESTED/PASS and owner-approved.

## Evidence

- Git commit `728d0775811f18d3251d8a0c0f01a46b5d7fb28b` was pulled successfully.
- Alembic upgraded from `0005_stage13_watchlists` to `0006_cr03_egusi_kwali`; `alembic current` confirmed head.
- Configured PostgreSQL/API/CRUD/access helper ended with `CR-03 OWNER SMOKE: PASS`.
- Public commodity, market, latest-price and history checks exposed only active Egusi/Kwali references.
- Existing registration, login, trial/subscription self-view, non-admin blocking and protected admin all-record paths passed.
- Admin temporary commodity/market create, deactivate, reactivate and cleanup passed.
- Admin temporary Egusi/Kwali price creation and cleanup passed without foreign-key failure.
- Runtime logs showed successful public, authentication, subscription and protected admin requests.

## Repair and retest

During manual browser testing, inactive Beans/Palm oil records and the Kwali record were accidentally deleted using approved Admin delete controls. This was detected from the HTTP 204 runtime logs before CR-03 approval.

The owner restored Beans and Palm oil as inactive and safely reran the reversible CR-03 data migration to recreate/reactivate Kwali and deactivate every other market. Final read-only database proof:

- Commodities: Egusi active; Beans inactive; Palm oil inactive.
- Markets: Kwali Market active; Abuja/FCT inactive; Nasarawa inactive; Benue inactive.
- Alembic: `0006_cr03_egusi_kwali (head)`.

No table, user, subscription, authentication record, audit log, access rule, application module or completed Stage 0–20 feature was removed.

## Approval

The owner instructed PriceYard to continue if the corrected output was okay. The corrected output passed, so CR-03 is approved and CR-04 Regression Testing only is authorized.
