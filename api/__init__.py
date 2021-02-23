from fastapi import APIRouter
from api import jingxi

router = APIRouter(prefix='/api')
router.include_router(jingxi.router)
