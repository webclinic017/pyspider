from typing import Optional

from fastapi import FastAPI
import api

app = FastAPI()
app.include_router(api.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
