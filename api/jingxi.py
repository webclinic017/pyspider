import ujson
from app.jingxi.keyword_search import KeywordSearch
from fastapi import APIRouter
from schemas.response import CommonResponse
from config import AioRedis

redis_instance = AioRedis()

router = APIRouter(prefix="/jingxi", tags=["jingxi"])


@router.get("/keywordSearch", response_model=CommonResponse)
async def keyword_search(keyword: str, page: int = 1):
    cache_key = f"{keyword}-{page}"
    redis_client = await redis_instance.setup()
    data = await redis_client.hget("jingxi_keyword_search_cache", cache_key)
    content = None
    if data:
        content = ujson.loads(data)
    else:
        async with KeywordSearch() as KS:
            res = await KS.request(keyword, page)
        if res:
            content = CommonResponse(data=res.json())
            await redis_client.hset(
                "jingxi_keyword_search_cache", cache_key, content.json()
            )
    await redis_instance.close()
    return content
