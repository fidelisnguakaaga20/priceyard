# Requirements Traceability Matrix

| Requirement ID | Source | Requirement | Scope Status | Implementation Stage | Files/Components | Test | Evidence | Status |
|---|---|---|---|---:|---|---|---|---|
| S0-01 | Reference/Execution | 14-day manual validation | MVP | 0 | Validation records | Date-range verification | Owner evidence + decision log | DEFERRED |
| S0-02 | Execution | Reach 50 people | MVP | 0 | Validation records | Participant count >= 50 | 65 reported | PASS |
| S0-03 | Execution | 10 active users | MVP | 0 | Validation records | Active count >= 10 | 14 replies reported | PASS |
| S0-04 | Execution | 5 willing to pay/paying | MVP | 0 | Validation records | Count >= 5 | 5 reported | PASS |
| S0-05 | Execution | At least 2 reliable independent price sources | MVP | 0 | Source records | Independence/reliability review | 2 source types reported; independent confirmation pending | DEFERRED |
| S0-06 | Reference | Track Egusi, Beans, Palm oil | MVP | 0 | Market sheet | Inspect records | Seed records | PASS |
| S0-07 | Reference | Track Abuja/FCT, Kwali, Nasarawa, Benue | MVP | 0 | Market sheet | Inspect coverage | Seed records / requested markets | IN PROGRESS |
| S0-08 | Reference | Structured market record fields | MVP | 0 | Market sheet | Inspect columns | Provided structured rows | PASS |
| S0-09 | Execution | Collect feedback evidence | MVP | 0 | Feedback summary | Inspect response totals | 14 replies; usefulness/trust/continuation/pay data | PASS |
| S0-10 | Execution | Maintain project status | MVP | 0 | docs/project-status.md | File review | Repository file | PASS |
| S1-01 | Execution | Create root project structure | MVP | 1 | repository | Tree inspection | docs/evidence/stage-1-tree.txt | PASS |
| S1-02 | Execution | Add governance files | MVP | 1 | docs/* | File existence/content review | repository | PASS |
| S1-03 | Execution | Ignore .env and secrets | MVP | 1 | .gitignore | git check-ignore | evidence file | PASS |
| S1-04 | Execution | Initialize Git and create first commit | MVP | 1 | .git | git log | `8a87c04b6d06e535458e1c07d06bf01cde4add19` | PASS |
| S2-01 | Execution | Create FastAPI application foundation | MVP | 2 | backend/app/main.py | Import/startup verification | docs/evidence/stage-2-import-check.txt; stage-2-uvicorn-output.txt | PASS |
| S2-02 | Execution | Add environment configuration | MVP | 2 | backend/app/config.py; backend/.env.example | Configuration import check | docs/evidence/stage-2-import-check.txt; stage-2-env-config-check.txt; stage-2-env-ignore-check.txt | PASS |
| S2-03 | Execution | Add backend requirements and verify dependencies | MVP | 2 | backend/requirements.txt | pip requirements verification | docs/evidence/stage-2-dependency-install.txt; stage-2-dependency-availability.txt | PASS |
| S2-04 | Execution | Add backend README | MVP | 2 | backend/README.md | File/content review | repository | PASS |
| S2-05 | Execution | Implement GET /health | MVP | 2 | backend/app/main.py | Live HTTP request | docs/evidence/stage-2-health-response.txt; stage-2-uvicorn-output.txt | PASS |
| S3-01 | Execution/Architecture | PostgreSQL connection and SQLAlchemy session foundation | MVP | 3 | backend/app/database.py; backend/app/config.py | Live SELECT 1 against PostgreSQL | Pending owner/local PostgreSQL verification | IN PROGRESS |
| S3-02 | Execution/Architecture | Alembic migration system | MVP | 3 | backend/alembic.ini; backend/migrations/* | Migration render + live upgrade head | PostgreSQL render PASS; live upgrade pending | IN PROGRESS |
| S3-03 | Execution | Create exactly 10 approved Stage 3 MVP tables | MVP | 3 | backend/app/models/*; initial migration | Metadata/table inspection + live DB inspection | Static metadata shows exactly 10 approved tables; live DB pending | IN PROGRESS |
| S3-04 | Execution | Verify model relationships/foreign keys | MVP | 3 | backend/app/models/* | SQLAlchemy mapper configuration and FK inspection | docs/evidence/stage-3-model-mapper-check.txt | PASS |
| S3-05 | Execution | `price_updates` supports required range/source/meaning/action/confidence fields | MVP | 3 | backend/app/models/price_update.py; migration | Required-column inspection | docs/evidence/stage-3-price-update-fields-check.txt | PASS |
| S3-06 | Execution | Deferred later-stage tables are not created | MVP | 3 | SQLAlchemy metadata; migration | Exact table-name scope check | docs/evidence/stage-3-schema-scope-check.txt | PASS |
