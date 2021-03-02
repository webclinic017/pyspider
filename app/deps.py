from fastapi import Depends, Request


def get_env(request: Request):
    return request.app.state.env


def get_client_session(request: Request):
    return request.app.state.session


def get_redis_local(request: Request):
    return request.app.state.redis


def get_redis15(request: Request):
    return request.app.state.redis15


def get_redis30(request: Request):
    return request.app.state.redis30


def get_tendis(request: Request):
    return request.app.state.tendis


class Depend:
    """
    全局依赖项
    """

    env = Depends(get_env)
    session = Depends(get_client_session)
    redis15 = Depends(get_redis15)
    redis30 = Depends(get_redis30)
    tendis = Depends(get_tendis)
