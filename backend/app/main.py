from fastapi import FastAPI

from app.config import get_settings
from app.routes.auth_routes import router as auth_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
