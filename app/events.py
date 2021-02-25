from loguru import logger
from config import AioRedis
from fastapi import FastAPI


r = AioRedis()
redis15 = AioRedis("aio_redis15")
redis30 = AioRedis("aio_redis30")


def setup_db(app: FastAPI, env="test"):
    async def connect_redis():
        app.state.env = env
        if env == "test":
            app.state.redis = await r.setup()
        elif env == "prod":
            app.state.redis15 = await redis15.setup()
            app.state.redis30 = await redis30.setup()
        logger.info("Redis connection established.")

    return connect_redis


def shutdown_db(app: FastAPI):
    async def stop_redis():
        env = app.state.env
        if env == "test":
            await r.close()
        elif env == "prod":
            await redis15.close()
            await redis30.close()
        logger.info("Redis Connection closed.")

    return stop_redis
