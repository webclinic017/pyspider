from app.jingxi.keyword_search import KeywordSearch
from fastapi import APIRouter
from schemas.response import CommonResponse

router = APIRouter(prefix="/jingxi", tags=["jingxi"])


@router.get("/keywordSearch", response_model=CommonResponse)
async def keyword_search(keyword: str, page: int = 1):
    async with KeywordSearch() as KS:
        res = await KS.request(keyword, page)
    if res:
        content = CommonResponse(data=res.json())
        return content
