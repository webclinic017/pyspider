import time
from pydantic import BaseModel
from typing import Any


class CommonResponse(BaseModel):
    data: dict
    code: int = 200
    msg: str = "success"


class CacheResponse(BaseModel):
    data: dict
    code: int = 200
    msg: str = "success"
    cache_time: int = int(time.time())


class EmptyResponse(BaseModel):
    data: Any = None
    code: int = 401
    msg: str = "false"
