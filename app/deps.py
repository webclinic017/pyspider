from fastapi import Depends, Request


def get_redis_local(request: Request):
    return request.app.state.redis


class DBDepend:
    redis_local = Depends(get_redis_local)
