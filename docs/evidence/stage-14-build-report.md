# Stage 14 Build Report — FAQ

1. Stage: 14 — FAQ.
2. Requirements covered: admin create/edit/publish/hide/delete; public published FAQ view; content restrictions; disclaimers.
3. Files changed: FAQ schema/service/routes, FastAPI router registration, governance/evidence docs.
4. Database: no migration; existing Stage 3 `faq_items` table reused.
5. APIs: GET /faq, GET /faq/{faq_id}, POST /faq, PATCH /faq/{faq_id}, PATCH /faq/{faq_id}/publish, PATCH /faq/{faq_id}/hide, DELETE /faq/{faq_id}.
6. Dependencies: none added.
7. Internal commands: Python compile/static/schema safety checks.
8. Expected: source compiles; safety guardrails accept approved disclaimer wording and reject explicit guarantees/private instructions.
9. Actual: internal checks PASS.
10. Tests prepared: owner Supabase-backed Stage 14 smoke.
11. Evidence: stage-14-static-check.txt, stage-14-compile-check.txt, stage-14-schema-safety-check.txt, stage-14-internal-api-check.txt, stage-14-owner-smoke.py.
12. Internal failures: native AI-container bcrypt package is unavailable.
13. Fix/retest: no project-code change was made for that environment limitation; an isolated temporary bcrypt compatibility stub was used only for an internal SQLite API-flow smoke, which passed. Owner environment remains the authority for runtime proof.
14. Outstanding: owner runtime proof required.
15. RTM: Stage 14 rows added; runtime rows IN PROGRESS.
16. Project status: Stage 14 BUILT/IN PROGRESS.
17. Scope: no Stage 15+ feature, migration, or dependency added.
18. Git: commit recorded after final checks.
19. Next stage after owner PASS+approval: Stage 15 — User Feedback and 1–5 Star Rating.
20. Gate: do not start Stage 15 until owner approval.

Editorial limitation: automated validation can block explicit guarantees and private contact/payment instructions, but cannot prove that text was not copied word-for-word from a paid source unless that source corpus is supplied. Human source review remains required by the Reference Document.
