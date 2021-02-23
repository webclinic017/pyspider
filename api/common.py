from pydantic import BaseModel


class CommonResponse(BaseModel):
    data: dict
    code: int = 200
    msg: str = "success"
