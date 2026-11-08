from pathlib import Path

root = Path(__file__).resolve().parents[2]
checks: dict[str, str] = {}


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"

model = (root / "backend/app/models/storage_suitability.py").read_text()
schema = (root / "backend/app/schemas/storage_suitability_schema.py").read_text()
service = (root / "backend/app/services/storage_suitability_service.py").read_text()
routes = (root / "backend/app/routes/storage_suitability_routes.py").read_text()
migration = (root / "backend/migrations/versions/0003_add_storage_suitability.py").read_text()
main = (root / "backend/app/main.py").read_text()
requirements = (root / "backend/requirements.txt").read_text()

check("storage_suitability model exists", '__tablename__ = "storage_suitability"' in model)
for field in (
    "commodity_id",
    "market_id",
    "price_update_id",
    "suitability_status",
    "import_risk",
    "oversupply_risk",
    "spoilage_risk",
    "buyer_availability",
    "quality_storage_notes",
    "summary",
    "created_at",
    "updated_at",
):
    check(f"model supports {field}", field in model)

check("approved statuses enforced in model", all(value in model for value in ("good", "watch", "risky", "not_recommended")))
check("approved statuses enforced in schema", 'Literal["good", "watch", "risky", "not_recommended"]' in schema)
check("storage disclaimer exact core wording present", "It does not guarantee profit, preservation, or future price increase." in schema)
check("storage guarantee claims rejected", "_FORBIDDEN_STORAGE_CLAIMS" in schema)
check("linked price update scope validation exists", "Linked price update must use the same commodity and market" in service)
check("admin create protected", 'Depends(require_roles("admin"))' in routes)
check("full-access view protected", "Depends(require_full_access)" in routes)
check("create/edit/view routes exist", all(token in routes for token in ('@router.post(', '@router.patch(', '@router.get(')) and '"/{item_id}"' in routes)
check("router registered", "app.include_router(storage_suitability_router)" in main)
check("Stage 11 migration revision correct", 'revision: str = "0003_stage11_storage_suitability"' in migration)
check("Stage 11 migration follows Stage 10", 'down_revision: Union[str, Sequence[str], None] = "0002_stage10_buy_sell_watch"' in migration)
check("Stage 11 migration creates only approved table", 'op.create_table(\n        "storage_suitability"' in migration and "cost_breakdowns" not in migration and "watchlists" not in migration)
check("no Stage 12 route introduced", "cost_breakdown" not in main)
check("no dependency added for Stage 11", "redis" not in requirements.lower() and "graphql" not in requirements.lower())

print(checks)
print("STAGE 11 STATIC CHECK: PASS")
