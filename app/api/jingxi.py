import ujson
from aioredis import Redis
from app.deps import get_redis
from app.schemas.response import CommonResponse
from app.src.jingxi.keyword_search import KeywordSearch
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/jingxi", tags=["jingxi"])


@router.get("/keywordSearch", response_model=CommonResponse)
async def keyword_search(
    keyword: str,
    page: int = 1,
    cache: Redis = Depends(get_redis),
):
    cache_key = f"{keyword}-{page}"
    data = await cache.hget("jingxi_keyword_search_cache", cache_key)
    if data:
        return ujson.loads(data)
    else:
        async with KeywordSearch() as KS:
            res = await KS.request(keyword, page)
        if res:
            content = CommonResponse(data=res.json())
            await cache.hset("jingxi_keyword_search_cache", cache_key, content.json())
            return content
