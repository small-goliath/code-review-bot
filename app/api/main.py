from fastapi import APIRouter

from app.api.routes import upsource

api_router = APIRouter()
api_router.include_router(upsource.router, prefix="/webhooks", tags=["webhooks"])