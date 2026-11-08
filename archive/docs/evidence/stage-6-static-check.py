from pathlib import Path

root = Path(__file__).resolve().parents[2]
checks: dict[str, bool] = {}

main = (root / "backend/app/main.py").read_text()
commodity_routes = (root / "backend/app/routes/commodity_routes.py").read_text()
market_routes = (root / "backend/app/routes/market_routes.py").read_text()
user_routes = (root / "backend/app/routes/user_routes.py").read_text()
subscription_routes = (root / "backend/app/routes/subscription_routes.py").read_text()
user_schema = (root / "backend/app/schemas/user_schema.py").read_text()
market_schema = (root / "backend/app/schemas/market_schema.py").read_text()
all_source = "\n".join(p.read_text() for p in (root / "backend/app").rglob("*.py"))

checks["main includes user router"] = "app.include_router(user_router)" in main
checks["main includes commodity router"] = "app.include_router(commodity_router)" in main
checks["main includes market router"] = "app.include_router(market_router)" in main
checks["commodity admin mutations protected"] = commodity_routes.count('Depends(require_roles("admin"))') == 3
checks["market admin mutations protected"] = market_routes.count('Depends(require_roles("admin"))') == 3
checks["user management admin protected"] = user_routes.count('Depends(require_roles("admin"))') == 3
checks["subscription admin update remains protected"] = 'Depends(require_roles("admin"))' in subscription_routes
checks["reporter role remains deferred"] = 'Literal["admin", "free_user", "paid_user"]' in user_schema and '"reporter"' not in user_schema
checks["market day validation supports weekdays"] = all(day in market_schema for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
checks["no Stage 7 price update API introduced"] = "/price-updates" not in all_source and "price_update_routes" not in main
checks["no forbidden infrastructure introduced"] = all(term not in all_source.lower() for term in ["redis", "graphql", "elasticsearch", "kubernetes", "celery"])

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"{name}: {'PASS' if ok else 'FAIL'}")
if failed:
    raise SystemExit("Failed checks: " + ", ".join(failed))
