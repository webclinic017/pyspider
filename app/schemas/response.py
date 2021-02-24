import time
from pydantic import BaseModel


class CommonResponse(BaseModel):
    data: dict
    code: int = 200
    msg: str = "success"


class CacheResponse(BaseModel):
    data: dict
    code: int = 200
    msg: str = "success"
    cache_time: int = int(time.time())
