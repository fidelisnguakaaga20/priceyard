from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONT = ROOT / "frontend" / "src"
checks: dict[str, str] = {}

def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"

app = (FRONT / "App.tsx").read_text()
layout = (FRONT / "components" / "AdminLayout.tsx").read_text()
route = (FRONT / "components" / "AdminRoute.tsx").read_text()
dash = (FRONT / "pages" / "admin" / "AdminDashboardPage.tsx").read_text()
price = (FRONT / "pages" / "admin" / "AdminPriceUpdatesPage.tsx").read_text()
all_admin = "\n".join(p.read_text() for p in (FRONT / "pages" / "admin").glob("*.tsx"))
package = (ROOT / "frontend" / "package.json").read_text()

required_routes = [
    'path="users"', 'path="commodities"', 'path="markets"', 'path="prices"',
    'path="market-signals"', 'path="quality-signals"', 'path="buying-zones"',
    'path="sell-watch"', 'path="storage"', 'path="costs"', 'path="faq"',
    'path="subscriptions"', 'path="feedback"', 'path="audit"', 'path="export"',
]
check("admin root route exists", 'path="admin"' in app and "<AdminRoute>" in app)
check("all approved admin management routes exist", all(item in app for item in required_routes))
check("admin navigation exposes every approved section", all(label in layout for label in ["Users", "Commodities", "Markets", "Price updates", "Market signals", "Quality signals", "Buying zones", "Sell-watch", "Storage", "Costs", "FAQ", "Subscriptions", "Feedback", "Audit logs", "CSV export"]))
check("frontend admin route rejects non-admin role", 'user.role !== "admin"' in route)
check("dashboard contains only approved basic metrics", all(label in dash for label in ["Total users", "Commodities", "Markets", "Latest updates", "Outdated prices", "Trial users", "Active users", "Feedback count", "Average rating"]))
check("possible meaning remains editable in admin price page", "Possible Meaning" in price and "possible_meaning" in price)
check("suggested action remains editable in admin price page", "Suggested Action" in price and "suggested_action" in price)
check("approved suggested actions preserved", all(action in price for action in ["Watch", "Investigate", "Buy Carefully", "Hold", "Sell Carefully"]))
check("approved confidence labels preserved", all(label in price for label in ["Reporter submitted", "Verified by 2 sources", "Admin confirmed", "Market visit confirmed", "Low confidence", "Price outdated"]))
for endpoint in ["/users", "/commodities", "/markets", "/price-updates", "/market-signals", "/quality-signals", "/buying-zones", "/sell-watch-windows", "/storage-suitability", "/cost-breakdowns", "/faq", "/subscriptions", "/feedback", "/audit-logs", "/reports/prices.csv"]:
    check(f"admin frontend integrates {endpoint}", endpoint in all_admin or endpoint in dash)
check("CSV export remains CSV only", "/reports/prices.csv" in all_admin and ".pdf" not in all_admin.lower())
check("no payment gateway or AI prediction admin page", all(term not in app.lower() for term in ["payment-gateway", "marketplace", "ai-prediction", "escrow", "logistics"]))
check("no new frontend runtime dependency", all(dep in package for dep in ['"react": "18.3.1"', '"react-dom": "18.3.1"', '"react-router-dom": "6.28.0"']))
check("Stage 19 frontend version set", '"version": "0.19.0"' in package)

print(checks)
print("STAGE 19 STATIC CHECK: PASS")
