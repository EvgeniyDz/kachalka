from fastapi import APIRouter

from app.api.routes.exercises import router as exercises_router
from app.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(exercises_router)
