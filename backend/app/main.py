from fastapi import FastAPI

from app.config import get_settings
from app.routes.auth_routes import router as auth_router
from app.routes.buying_zone_routes import router as buying_zone_router
from app.routes.commodity_routes import router as commodity_router
from app.routes.cost_breakdown_routes import router as cost_breakdown_router
from app.routes.market_routes import router as market_router
from app.routes.market_signal_routes import router as market_signal_router
from app.routes.price_update_routes import router as price_update_router
from app.routes.quality_signal_routes import router as quality_signal_router
from app.routes.sell_watch_window_routes import router as sell_watch_window_router
from app.routes.storage_suitability_routes import router as storage_suitability_router
from app.routes.subscription_routes import router as subscription_router
from app.routes.user_routes import router as user_router
from app.routes.watchlist_routes import router as watchlist_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(auth_router)
app.include_router(subscription_router)
app.include_router(user_router)
app.include_router(commodity_router)
app.include_router(market_router)
app.include_router(price_update_router)
app.include_router(market_signal_router)
app.include_router(quality_signal_router)
app.include_router(buying_zone_router)
app.include_router(sell_watch_window_router)
app.include_router(storage_suitability_router)
app.include_router(cost_breakdown_router)
app.include_router(watchlist_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
