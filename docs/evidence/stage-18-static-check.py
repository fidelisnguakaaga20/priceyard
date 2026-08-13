from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
checks: dict[str, bool] = {}

required = [
    "src/App.tsx",
    "src/main.tsx",
    "src/styles.css",
    "src/pages/HomePage.tsx",
    "src/pages/PricesPage.tsx",
    "src/pages/CommodityDetailPage.tsx",
    "src/pages/PriceHistoryPage.tsx",
    "src/pages/MarketDaysPage.tsx",
    "src/pages/FAQPage.tsx",
    "src/pages/FeedbackPage.tsx",
    "src/pages/LoginPage.tsx",
    "src/pages/RegisterPage.tsx",
    "src/pages/DashboardPage.tsx",
    "src/pages/WatchlistPage.tsx",
]
for rel in required:
    checks[f"required frontend file {rel}"] = (FRONTEND / rel).exists()

app = (FRONTEND / "src/App.tsx").read_text(encoding="utf-8")
for route in ["prices", "commodities/:commodityName", "history", "market-days", "faq", "feedback", "login", "register", "dashboard", "watchlist"]:
    checks[f"Stage 18 route {route}"] = route in app

package = (FRONTEND / "package.json").read_text(encoding="utf-8")
checks["React dependency declared"] = '"react"' in package and '"react-dom"' in package
checks["TypeScript build declared"] = '"typescript"' in package and '"build": "tsc -b && vite build"' in package
checks["Vite development integration declared"] = '"vite"' in package

all_source = "\n".join(p.read_text(encoding="utf-8") for p in (FRONTEND / "src").rglob("*") if p.is_file())
checks["Possible Meaning remains visible"] = "Possible Meaning" in all_source
checks["Suggested Action remains visible"] = "Suggested Action" in all_source
checks["price range visible"] = "price_low" in all_source and "price_high" in all_source
checks["previous range visible"] = "previous_price_low" in all_source and "previous_price_high" in all_source
checks["movement visible"] = "movement" in all_source
checks["confidence visible"] = "confidence_level" in all_source
checks["last updated visible"] = "Last updated" in all_source
checks["market signals integrated"] = "/market-signals" in all_source
checks["quality signals integrated"] = "/quality-signals" in all_source
checks["storage suitability integrated"] = "/storage-suitability" in all_source
checks["buying zones integrated"] = "/buying-zones" in all_source
checks["sell-watch integrated"] = "/sell-watch-windows" in all_source
checks["cost breakdown integrated"] = "/cost-breakdowns" in all_source
checks["watchlist API integrated"] = "/watchlist" in all_source
checks["feedback API integrated"] = "/feedback" in all_source
checks["auth APIs integrated"] = "/auth/login" in all_source and "/auth/register" in all_source and "/auth/me" in all_source
checks["subscription access integrated"] = "/subscriptions/" in all_source

price_disclaimer = "Prices are market estimates and may change based on quality, quantity, negotiation, transport cost, bag size, time of day, and market conditions. PriceYard provides market information only and does not guarantee profit or exact transaction prices."
market_disclaimer = "Market signals are observations based on available market information. They are not guaranteed predictions or financial advice. Users should verify before making major buying, selling, or storage decisions."
storage_disclaimer = "Storage suitability is based on available market and quality information. It does not guarantee profit, preservation, or future price increase."
checks["required price disclaimer exact"] = price_disclaimer in all_source
checks["required market disclaimer exact"] = market_disclaimer in all_source
checks["required storage disclaimer exact"] = storage_disclaimer in all_source
checks["private price source identities not consumed by frontend"] = "source_1" not in all_source and "source_2" not in all_source
checks["no admin frontend route"] = not re.search(r'path=["\']admin', app, re.I)
checks["target-price alerts remain deferred"] = "target_price" not in all_source
checks["no payment gateway frontend"] = "card number" not in all_source.lower() and "payment gateway" not in all_source.lower()
checks["responsive mobile CSS present"] = "@media (max-width: 640px)" in (FRONTEND / "src/styles.css").read_text(encoding="utf-8")
checks["local API proxy present"] = '"/api"' in (FRONTEND / "vite.config.ts").read_text(encoding="utf-8")
checks["production API environment variable present"] = "VITE_API_URL" in (FRONTEND / ".env.example").read_text(encoding="utf-8")

migration_files = sorted((ROOT / "backend/migrations/versions").glob("*.py"))
checks["Stage 18 adds no database migration"] = any("0005" in p.name for p in migration_files) and not any("0006" in p.name for p in migration_files)

failed = [name for name, ok in checks.items() if not ok]
print(checks)
print("STAGE 18 STATIC CHECK:", "PASS" if not failed else "FAIL")
if failed:
    print("FAILED:", failed)
    raise SystemExit(1)
