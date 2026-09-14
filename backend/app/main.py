from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.rate_limit import limiter
from app.routes.audit_log_routes import router as audit_log_router
from app.routes.auth_routes import router as auth_router
from app.routes.buying_zone_routes import router as buying_zone_router
from app.routes.commodity_routes import router as commodity_router
from app.routes.cost_breakdown_routes import router as cost_breakdown_router
from app.routes.faq_routes import router as faq_router
from app.routes.feedback_routes import router as feedback_router
from app.routes.feedback_routes import testimonials_router
from app.routes.market_routes import router as market_router
from app.routes.market_signal_routes import router as market_signal_router
from app.routes.price_update_routes import router as price_update_router
from app.routes.quality_signal_routes import router as quality_signal_router
from app.routes.report_export_routes import router as report_export_router
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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = [
    origin.strip().rstrip("/")
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(audit_log_router)
app.include_router(subscription_router)
app.include_router(user_router)
app.include_router(commodity_router)
app.include_router(market_router)
app.include_router(price_update_router)
app.include_router(market_signal_router)
app.include_router(quality_signal_router)
app.include_router(report_export_router)
app.include_router(buying_zone_router)
app.include_router(sell_watch_window_router)
app.include_router(storage_suitability_router)
app.include_router(cost_breakdown_router)
app.include_router(faq_router)
app.include_router(feedback_router)
app.include_router(testimonials_router)
app.include_router(watchlist_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
