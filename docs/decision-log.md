# Decision Log

## DEC-001 — Stage 0 coding override
- Date: 2026-08-12
- Current requirement: Stage 0 must pass all validation criteria before coding.
- Source: PriceYard Reference Document + AI Project Execution Plan.
- Owner evidence: 65 reached; 14 replies; 5 willing to pay; positive feedback; two source types.
- Exception: Owner stated the 14-day validation completion was mock/form-testing evidence and that independent source confirmation remained later work, while explicitly setting `Application Coding Permission: YES`.
- Decision: Permit Stage 1 to begin under owner-approved business-risk exception.
- Database effect: None.
- API effect: None.
- Frontend effect: None.
- Test effect: Stage 0 final acceptance remains unresolved and must be reconciled before Stage 24.
- Completed-stage effect: None.
- Approval: Owner-approved in conversation.

## DEC-002 — Stage 1 approval and Stage 2 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 1 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner instruction: After receiving the Stage 1 PASS report and repository, the owner instructed the AI to continue based on the approved execution plan.
- Decision: Treat the instruction to continue as owner approval of Stage 1 and authorization to execute Stage 2 only.
- Database effect: None.
- API effect: Authorizes only the Stage 2 health endpoint.
- Frontend effect: None.
- Test effect: Stage 2 proof must be completed before Stage 3.
- Completed-stage effect: Stage 1 becomes completed/approved.
- Approval: Owner instruction in conversation.

## DEC-003 — Stage 2 owner approval and Stage 3 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 2 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner instruction: `approved` after local dependency installation, Uvicorn startup, and `GET /health` returned HTTP 200 on the owner's computer.
- Decision: Stage 2 is owner-verified and approved. Stage 3 — Database Foundation is authorized.
- Database effect: Authorizes only the approved Stage 3 database foundation.
- API effect: None; no new business API is authorized in Stage 3.
- Frontend effect: None.
- Test effect: Stage 3 requires PostgreSQL connection, migration, table, relationship, and required-field proof before completion.
- Completed-stage effect: Stage 2 becomes completed and owner-approved.
- Approval: Owner-approved in conversation.

## DEC-004 — Stage 3 approval and Stage 4 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 3 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner instruction: `approved` after the owner's live Supabase PostgreSQL connection, Alembic migration, table inspection, and `price_updates` field inspection passed.
- Decision: Stage 3 is owner-verified and approved. Stage 4 — Authentication is authorized.
- Database effect: No Stage 4 schema change required; the approved `users` table already contains the required authentication fields.
- API effect: Authorizes only `POST /auth/register`, `POST /auth/login`, and `GET /auth/me` for Stage 4.
- Frontend effect: None.
- Test effect: Stage 4 must prove registration, duplicate rejection, login, wrong-password rejection, inactive-user blocking, JWT handling, `/auth/me`, bcrypt storage, and password-hash non-disclosure.
- Completed-stage effect: Stage 3 becomes completed and owner-approved.
- Approval: Owner-approved in conversation.

## DEC-005 — Stage 4 approval and Stage 5 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 4 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: `STAGE 4 OWNER SMOKE: PASS` with all 17 approved authentication checks passing on the owner's configured Supabase PostgreSQL environment.
- Owner instruction: `continue base on this execution plan here` after the successful Stage 4 smoke proof.
- Decision: Treat the instruction to continue as owner approval of Stage 4 and authorization to execute Stage 5 — Subscription and 14-Day Trial only.
- Database effect: Stage 5 uses the existing `subscriptions` table; no schema change is required unless testing reveals an approved requirement cannot be met.
- API effect: Authorizes only the approved subscription/trial APIs and access-status logic for Stage 5.
- Frontend effect: None.
- Test effect: Stage 5 must prove 14-day trial timing, full/limited access classification, active paid access, invalid-status rejection, and admin subscription update.
- Completed-stage effect: Stage 4 becomes RETESTED/PASS and owner-approved.
- Approval: Owner instruction in conversation.

## DEC-006 — Stage 5 approval and Stage 6 authorization
- Date: 2026-08-12
- Current requirement: Do not proceed from Stage 5 until owner approval.
- Source: PriceYard AI Project Execution Plan.
- Owner proof: Corrected `STAGE 5 OWNER SMOKE: PASS` with all 31 approved subscription/trial checks passing on the owner's configured Supabase PostgreSQL environment.
- Owner instruction: `approved`.
- Decision: Stage 5 is RETESTED/PASS and owner-approved. Stage 6 — Admin Core Management is authorized.
- Database effect: No schema change is expected; Stage 6 uses existing `users`, `commodities`, `markets`, and `subscriptions` tables.
- API effect: Authorizes only admin authorization, user management, commodity management, market management, and approved subscription management.
- Frontend effect: None.
- Test effect: Stage 6 must prove non-admin blocking, admin commodity CRUD, admin market CRUD, user management, and subscription management.
- Completed-stage effect: Stage 5 becomes RETESTED/PASS and owner-approved.
- Approval: Owner-approved in conversation.
