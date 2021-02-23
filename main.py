from fastapi import FastAPI
from databases import Database
import api

app = FastAPI()
app.include_router(api.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
