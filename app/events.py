from loguru import logger
from config import AioRedis
from fastapi import FastAPI


r = AioRedis()


def setup_db(app: FastAPI):
    async def connect_redis():
        app.state.redis = await r.setup()
        logger.info("Redis connection established")

    return connect_redis


def shutdown_db():
    async def stop_redis():
        await r.close()
        logger.info("Redis Connection closed")

    return stop_redis
