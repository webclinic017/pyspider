from fastapi import FastAPI
import api
import asyncio
from config import AioRedis

r = AioRedis()

app = FastAPI()
app.include_router(api.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# @app.on_event("startup")
# async def setup():
#     global client
#     client = await r.setup()


# @app.get("/test")
# async def test():
#     await client.set("test", "fastapi")
#     return await client.get("test")


# @app.on_event("shutdown")
# async def stop():
#     await r.close()


# loop = asyncio.get_event_loop()
# loop.run_until_complete(test())
