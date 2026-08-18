"""Stage 20 pre-fix static access-control assessment.

This script does not modify application behavior. It records which approved
Stage 20 controls are already present and identifies access leaks that require
Change Control approval before implementation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda p: (ROOT / p).read_text(encoding="utf-8")

checks: dict[str, str] = {}

def check(name: str, condition: bool, *, expected_fail: bool = False) -> None:
    if expected_fail:
        checks[name] = "FAIL (expected pre-fix)" if not condition else "UNEXPECTED PASS"
    else:
        checks[name] = "PASS" if condition else "FAIL"

permissions = read("backend/app/utils/permissions.py")
subscription = read("backend/app/services/subscription_service.py")
price_schema = read("backend/app/schemas/price_update_schema.py")
market_schema = read("backend/app/schemas/market_signal_schema.py")
market_routes = read("backend/app/routes/market_signal_routes.py")
quality_routes = read("backend/app/routes/quality_signal_routes.py")
buying_routes = read("backend/app/routes/buying_zone_routes.py")
sell_routes = read("backend/app/routes/sell_watch_window_routes.py")
storage_routes = read("backend/app/routes/storage_suitability_routes.py")
cost_routes = read("backend/app/routes/cost_breakdown_routes.py")
feedback_routes = read("backend/app/routes/feedback_routes.py")
watchlist_routes = read("backend/app/routes/watchlist_routes.py")
admin_routes = "\n".join(read(p) for p in [
    "backend/app/routes/user_routes.py",
    "backend/app/routes/audit_log_routes.py",
    "backend/app/routes/report_export_routes.py",
])

check("inactive accounts are rejected by backend current-user dependency", "if not user.is_active:" in permissions and "User account is inactive" in permissions)
check("admin role has full-access bypass", 'current_user.role == "admin"' in permissions)
check("active paid status is full access", 'subscription.status == "active"' in subscription)
check("trial access expires by time", 'current_time < trial_end' in subscription and 'subscription.status = "expired"' in subscription)
check("free/cancelled/expired are not classified full-access", 'if subscription.status == "active"' in subscription and 'if subscription.status != "trial"' in subscription)
check("buying zones use backend full-access guard", "Depends(require_full_access)" in buying_routes)
check("sell-watch uses backend full-access guard", "Depends(require_full_access)" in sell_routes)
check("storage suitability uses backend full-access guard", "Depends(require_full_access)" in storage_routes)
check("cost breakdown uses backend full-access guard", "Depends(require_full_access)" in cost_routes)
check("feedback submission requires authenticated active user", "Depends(get_current_user)" in feedback_routes)
check("watchlist requires authenticated active user", "Depends(get_current_user)" in watchlist_routes)
check("admin APIs use admin role guards", 'require_roles("admin")' in admin_routes)

# Approved Stage 20 gaps. These are deliberately reported as FAIL until the
# owner approves the smallest access-control correction under Change Control.
public_price_limited = (
    "possible_meaning" not in price_schema[price_schema.index("class PriceUpdatePublicResponse"):price_schema.index("class PriceUpdateAdminResponse")]
    and "suggested_action" not in price_schema[price_schema.index("class PriceUpdatePublicResponse"):price_schema.index("class PriceUpdateAdminResponse")]
)
check("guest public price payload excludes deeper premium guidance", public_price_limited, expected_fail=True)

market_basic_only = (
    "possible_meaning" not in market_schema[market_schema.index("class MarketSignalResponse"):]
    and "suggested_action" not in market_schema[market_schema.index("class MarketSignalResponse"):]
)
check("limited-user market signal payload is basic only", market_basic_only, expected_fail=True)

quality_full_guard = "Depends(require_full_access)" in quality_routes
check("quality signals require full approved access", quality_full_guard, expected_fail=True)

for key, value in checks.items():
    print(f"{key}: {value}")

required_pass = [v for v in checks.values() if v == "FAIL"]
expected_fails = [v for v in checks.values() if v == "FAIL (expected pre-fix)"]
if required_pass:
    raise SystemExit("STAGE 20 STATIC ASSESSMENT: FAIL — unexpected regression")
if len(expected_fails) != 3:
    raise SystemExit("STAGE 20 STATIC ASSESSMENT: FAIL — expected access-gap set changed")
print("STAGE 20 STATIC ASSESSMENT: COMPLETE — 3 APPROVED-REQUIREMENT GAPS REQUIRE CHANGE CONTROL")
