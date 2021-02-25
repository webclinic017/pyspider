from fastapi import Depends, Request


def get_redis_local(request: Request):
    return request.app.state.redis


def get_redis15(request: Request):
    return request.app.state.redis15


def get_redis30(request: Request):
    return request.app.state.redis30


class DBDepend:
    redis_local = Depends(get_redis_local)
    redis15 = Depends(get_redis15)
    redis30 = Depends(get_redis30)
