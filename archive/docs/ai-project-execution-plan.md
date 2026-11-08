# PriceYard AI Project Execution Plan — Repository Control Copy

## Master instruction
Use the approved PriceYard Official Reference Document, PriceYard Architecture Design and this Execution Plan as sources of truth, in that authority order. Choose the simplest compliant solution. Do not invent requirements, change stack, add future features or skip stages.

## Execution cycle
Requirement → Implementation → Test → Proof → Fix → Retest → Documentation → Traceability Update → Approval.

After every stage record requirements covered, changed files, DB/API/dependency changes, commands, expected/actual result, tests, proof, failures, fixes/retests, outstanding issues, traceability/status updates, scope confirmation, git commit and next stage. Generated-code claims are not proof.

## Anti-drift controls
Do not change product name/direction, initial commodities/markets, stack, roles/access, trial/subscription rules, disclaimers, approved folder structure/API contracts/database schema without owner-approved change control. Fix the smallest affected area and do not rewrite working modules unnecessarily.

## Governance files
Maintain: reference document; architecture design; execution plan; requirements traceability matrix; project status; decision log; database schema; API endpoints; deployment plan; development roadmap; evidence directory.

## Change control
Before any add/remove/rename/change/bypass, report current requirement, source, proposed change, reason, DB/API/frontend/test/completed-stage effects and approval needed. Do not implement until approved.

## Stage order
0. 14-day WhatsApp/manual MVP validation
1. Project setup
2. Backend foundation
3. Database foundation
4. Authentication
5. Subscription and 14-day trial
6. Admin core management
7. Price updates
8. Search, filters, history, comparison
9. Market and quality signals
10. Buying zones and sell-watch windows
11. Storage suitability
12. Cost breakdown
13. Watchlist
14. FAQ
15. User feedback / 1–5 stars
16. Audit logs
17. Simple CSV export
18. Public/user frontend MVP
19. Admin frontend MVP
20. Access-control/subscription testing
21. Full MVP testing/security review
22. Deployment
23. Pilot launch
24. Final acceptance audit

## Stage gate
Never move to the next stage without owner approval. Never combine stages without approval. Never declare MVP complete before Stage 24 passes.

## Stage 0 pass criteria
14 days completed; 50 people reached/joined; 10 active; 5 willing-to-pay/paying; at least 2 reliable price sources; demand evidence documented; RTM created; project status updated.

## Required development constraints carried forward
- `possible_meaning` and `suggested_action` must never disappear.
- Backend authorization is authoritative; frontend hiding is not security.
- Private source identities and secrets must not leak.
- No guaranteed predictions, financial advice or profit claims.
- Low-confidence data must not be represented as verified.

## Deferred features
AI prediction; guaranteed prediction; marketplace; transactions; escrow; payment gateway; card storage; logistics; native mobile; SMS/WhatsApp alerts; complex charts; reporter portal/reputation; verified directory; AI trading advice/automatic decisions; loan advice; profit guarantees; complex average-cost/profit calculators; automated PDF reports; API/data subscription; advanced reporter media workflow.
