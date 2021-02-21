from typing import Optional

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(on_startup=[])


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Optional[str] = None):
#     content = {"item_id": item_id, "q": q}
#     return ORJSONResponse(content)


items = {}


@app.on_event("startup")
async def startup_event():
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}


@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]
