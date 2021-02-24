from config import AioRedis
from fastapi import Depends


async def redis_local():
    r = AioRedis()
    redis_client = await r.setup()
    yield redis_client
    await r.close()


class DBDepend:
    redis_local = Depends(redis_local)
