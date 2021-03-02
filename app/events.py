from aiohttp import ClientSession, TCPConnector
from config import AioRedis, TendisClient
from fastapi import FastAPI
from loguru import logger

r = AioRedis()
redis15 = AioRedis("aio_redis15")
redis30 = AioRedis("aio_redis30")
tendis = TendisClient()


def setup_db(app: FastAPI, env="test"):
    async def setup_depends():
        app.state.session = ClientSession(connector=TCPConnector(ssl=False))
        logger.info("client session created.")
        app.state.env = env
        if env == "test":
            app.state.redis = await r.setup()
            app.state.redis15 = app.state.redis
            app.state.redis30 = app.state.redis
        elif env == "prod":
            app.state.redis15 = await redis15.setup()
            app.state.redis30 = await redis30.setup()
            app.state.tendis = tendis
        logger.info("db connection established.")

    return setup_depends


def shutdown_db(app: FastAPI):
    async def stop_depends():
        await app.state.session.close()
        logger.info("client session closed.")
        env = app.state.env
        if env == "test":
            await r.close()
        elif env == "prod":
            await redis15.close()
            await redis30.close()
            tendis.shutdown()
        logger.info("db connection closed.")

    return stop_depends
