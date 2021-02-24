from fastapi import APIRouter

from app.api import jingxi

router = APIRouter(prefix="/api")
router.include_router(jingxi.router)
