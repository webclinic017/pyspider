from app.jingxi.keyword_search import KeywordSearch
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter(prefix="/jingxi", tags=["jingxi"])


@router.get("/keywordSearch")
async def keyword_search(keyword: str, page: int = 1):
    async with KeywordSearch() as KS:
        data = await KS.request(keyword, page)
    if data:
        return ORJSONResponse(data.json())
