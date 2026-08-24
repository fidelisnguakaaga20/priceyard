"""Static CR-03 scope, migration, query, and UI contract verification."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


results: dict[str, str] = {}


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    results[label] = "PASS"


commodity_model = read("backend/app/models/commodity.py")
market_model = read("backend/app/models/market.py")
commodity_service = read("backend/app/services/commodity_service.py")
market_service = read("backend/app/services/market_service.py")
commodity_routes = read("backend/app/routes/commodity_routes.py")
market_routes = read("backend/app/routes/market_routes.py")
price_service = read("backend/app/services/price_update_service.py")
price_routes = read("backend/app/routes/price_update_routes.py")
migration = read("backend/migrations/versions/0006_focus_egusi_kwali.py")
prices_page = read("frontend/src/pages/PricesPage.tsx")
admin_commodities = read("frontend/src/pages/admin/AdminCommoditiesPage.tsx")
admin_markets = read("frontend/src/pages/admin/AdminMarketsPage.tsx")
admin_dashboard = read("frontend/src/pages/admin/AdminDashboardPage.tsx")
admin_prices = read("frontend/src/pages/admin/AdminPriceUpdatesPage.tsx")

expect("is_active: Mapped[bool]" in commodity_model, "commodities already use is_active")
expect("is_active: Mapped[bool]" in market_model, "markets already use is_active")
expect('down_revision: Union[str, Sequence[str], None] = "0005_stage13_watchlists"' in migration, "migration follows approved head")
expect('name="Egusi"' in migration and 'name="Kwali Market"' in migration, "migration ensures focus records exist")
expect(migration.count("values(is_active=False)") == 2, "migration deactivates prior commodity and market sets")
expect('values(name="Egusi", is_active=True)' in migration, "migration activates canonical Egusi")
expect('values(name="Kwali Market", is_active=True)' in migration, "migration activates canonical Kwali Market")
expect("op.drop_" not in migration and "sa.delete" not in migration, "migration deletes no table or business record")
expect(all(name not in migration for name in ("users", "subscriptions", "audit_logs")), "migration does not touch user/auth/subscription/audit data")

expect("active_only: bool = False" in commodity_service and "Commodity.is_active.is_(True)" in commodity_service, "commodity service supports active-only public listing")
expect("active_only: bool = False" in market_service and "Market.is_active.is_(True)" in market_service, "market service supports active-only public listing")
expect("list_commodities(db, active_only=True)" in commodity_routes, "public commodity list is active-only")
expect("list_markets(db, active_only=True)" in market_routes, "public market list is active-only")
expect('@router.get("/admin/all"' in commodity_routes and 'Depends(require_roles("admin"))' in commodity_routes, "all-commodity view is admin protected")
expect('@router.get("/admin/all"' in market_routes and 'Depends(require_roles("admin"))' in market_routes, "all-market view is admin protected")
expect(all(action in commodity_routes for action in ('@router.post(""', '@router.patch("/{commodity_id}"', '@router.delete("/{commodity_id}"')), "commodity CRUD remains intact")
expect(all(action in market_routes for action in ('@router.post(""', '@router.patch("/{market_id}"', '@router.delete("/{market_id}"')), "market CRUD remains intact")

expect("Commodity.is_active.is_(True), Market.is_active.is_(True)" in price_service, "public approved-price queries require active commodity and market")
expect("active_only=False" in price_service and "list_admin_approved_price_history" in price_service, "admin history preserves inactive-record management visibility")
expect('@router.get("/admin/history"' in price_routes and 'Depends(require_roles("admin"))' in price_routes, "all-price history is admin protected")
expect("Commodity is inactive" in price_service and "Market is inactive" in price_service, "price creation still rejects inactive references")

expect('apiFetch<Commodity[]>("/commodities")' in prices_page, "public commodity filter loads active API data")
expect('apiFetch<Market[]>("/markets")' in prices_page, "public market filter loads active API data")
expect("<select value={commodity}" in prices_page, "commodity filter is an active-record select")
expect('useAdminList<Commodity>("/commodities/admin/all")' in admin_commodities, "admin commodity page can manage all records")
expect('useAdminList<Market>("/markets/admin/all")' in admin_markets, "admin market page can manage all records")
expect('"/commodities/admin/all"' in admin_dashboard and '"/markets/admin/all"' in admin_dashboard, "admin dashboard keeps all-record counts")
expect('useAdminList<PriceUpdate>("/price-updates/admin/history")' in admin_prices, "admin price page preserves all approved history")

print(results)
print("CR-03 STATIC CHECK: PASS")
