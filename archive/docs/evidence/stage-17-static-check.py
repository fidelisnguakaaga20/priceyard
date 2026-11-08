from pathlib import Path

root = Path(__file__).resolve().parents[2]
service = (root / "backend/app/services/report_export_service.py").read_text()
route = (root / "backend/app/routes/report_export_routes.py").read_text()
main = (root / "backend/app/main.py").read_text()
requirements = (root / "backend/requirements.txt").read_text()
checks = {
    "CSV service exists": "build_price_report_csv" in service,
    "approved price filter exists": 'PriceUpdate.status == "approved"' in service,
    "commodity filter exists": "Commodity.name.ilike" in service,
    "market filter exists": "Market.name.ilike" in service,
    "date-from filter exists": "date_from" in service,
    "date-to filter exists": "date_to" in service,
    "date order validation exists": "date_from > date_to" in service,
    "possible meaning CSV header exists": '"possible_meaning"' in service,
    "suggested action CSV header exists": '"suggested_action"' in service,
    "market signals CSV header exists": '"market_signals"' in service,
    "quality signals CSV header exists": '"quality_signals"' in service,
    "source 1 is not a CSV header": '"source_1"' not in service.split("CSV_HEADERS =",1)[1].split("]",1)[0],
    "source 2 is not a CSV header": '"source_2"' not in service.split("CSV_HEADERS =",1)[1].split("]",1)[0],
    "admin-only route": 'Depends(require_roles("admin"))' in route,
    "CSV route registered": "report_export_router" in main,
    "no CSV dependency added": "pandas" not in requirements.lower(),
}
failed = [name for name, passed in checks.items() if not passed]
print(checks)
if failed:
    raise SystemExit("FAILED: " + ", ".join(failed))
print("STAGE 17 STATIC CHECK: PASS")
