import ujson
from aioredis import Redis
from app.constants import JingXi
from app.deps import DBDepend, session
from app.schemas.response import CommonResponse, EmptyResponse
from app.src.jingxi.keyword_search import KeywordSearch
from fastapi import APIRouter

router = APIRouter(prefix="/jingxi", tags=["jingxi"])


@router.get("/keywordSearch", response_model=CommonResponse, name="关键词搜索")
async def keyword_search(
    keyword: str,
    page: int = 1,
    cache: Redis = DBDepend.redis30,
    session=session,
):
    cache_key = f"{keyword}-{page}"
    data = await cache.hget(JingXi.KEYWORD_SEARCH_CACHE_HASH, cache_key)
    if data:
        return ujson.loads(data)
    else:
        KS = KeywordSearch(session)
        res = await KS.request(keyword, page)
        if res:
            content = CommonResponse(data=res.json())
            await cache.hset(
                JingXi.KEYWORD_SEARCH_CACHE_HASH, cache_key, content.json()
            )
            return content
        return EmptyResponse()
