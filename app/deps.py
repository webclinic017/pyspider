from config import AioRedis
from fastapi import Depends, Request


async def redis_local():
    r = AioRedis()
    redis_client = await r.setup()
    yield redis_client
    await r.close()


def get_redis_local(request: Request):
    return request.app.state.redis


class DBDepend:
    redis_local = Depends(get_redis_local)
