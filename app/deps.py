from config import AioRedis

r = AioRedis()


async def get_redis():
    redis_client = await r.setup()
    yield redis_client
    await r.close()
