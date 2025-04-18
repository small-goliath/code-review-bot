from fastapi import APIRouter

from app.api.routes import upsource, gitlab

api_router = APIRouter()
api_router.include_router(upsource.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(gitlab.router, prefix="/webhooks", tags=["webhooks"])