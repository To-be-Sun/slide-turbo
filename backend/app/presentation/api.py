"""
API ルーター集約
全ドメインのルーターを /api/v1 にマウントする。
"""

from fastapi import APIRouter

from app.presentation.routers.outline_router import router as outline_router
from app.presentation.routers.slide_router import router as slide_router
from app.presentation.routers.template_router import router as template_router
from app.presentation.routers.user_router import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user_router)
api_router.include_router(template_router)
api_router.include_router(slide_router)
api_router.include_router(outline_router)
