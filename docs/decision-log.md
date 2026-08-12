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
