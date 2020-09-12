import logging
import logging.handlers
import os
import random

import redis


def get_logger(file_name):
    """获取日志记录器

    Args:
        file_name (str): [记录日志的文件名]

    Returns:
        [obj]: [logger对象]
    """
    logger = logging.getLogger(file_name)
    if not file_name.endswith('.log'):
        file_name = file_name + '.log'
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(filename)s %(lineno)s %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_path = 'logs/' + file_name
    handler = logging.handlers.RotatingFileHandler(file_path,
                                                   maxBytes=1024 * 1024)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


async def get_proxy(session, platform='zhilian'):
    """获取代理

    Args:
        platform (str, optional): [使用的代理平台]. Defaults to 'zhilian'.

    Returns:
        [str]: [proxy]
    """
    if platform == 'zhilian':
        return 'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
    url = 'http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1'.format(
        platform)
    try:
        async with session.request('GET', url) as res:
            result = await res.json()
    except Exception as e:
        # logger.exception(str(e))
        print(e)
        return None
    else:
        proxy = result.get('data')
        if proxy:
            return 'http://' + proxy
        return None


def init_redis_client(host='localhost', port=6379, password=None, db=0):
    """连接redis

    Args:
        host (str, optional):  Defaults to 'localhost'.
        port ([type], optional): Defaults to None.
        password ([type], optional): Defaults to None.
        db (int, optional): Defaults to 0.

    Returns:
        obj: [redis连接对象]
    """
    try:
        pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    db=db,
                                    password=password,
                                    decode_responses=True)
        client = redis.Redis(connection_pool=pool)
    except Exception as e:
        print(e)
        return None
    return client


async def get_ua(session, platform='mobile'):
    """获取任意ua

    Args:
        platform (str, optional): Defaults to 'mobile'.

    Returns:
        [type]: [description]
    """
    random_ua_links = [
        "http://ycrawl.91cyt.com/api/v1/pdd/common/randomIosUa",
        "http://ycrawl.91cyt.com/api/v1/pdd/common/randomAndroidUa",
    ]
    url = random.choice(random_ua_links)
    if platform == 'web':
        url = "http://ycrawl.91cyt.com/api/v1/pdd/common/randomUa"
    try:
        async with session.get(url) as resp:
            res = await resp.json()
        ua = res['data']
        return ua
    except Exception as e:
        print(e)
        return False


async def start_request(session,
                        url,
                        method='GET',
                        headers=None,
                        proxy=None,
                        data=None,
                        timeout=3,
                        return_type='json'):
    """发起通用请求，返回response

    Args:
        session ([type]): [description]
        url ([type]): [description]
        method (str, optional): [description]. Defaults to 'GET'.
        headers ([type], optional): [description]. Defaults to None.
        proxy ([type], optional): [description]. Defaults to None.
        data ([type], optional): [description]. Defaults to None.
        timeout (int, optional): [description]. Defaults to 3.

    Returns:
        [type]: [description]
    """
    try:
        async with session.request(method,
                                   url,
                                   headers=headers,
                                   proxy=proxy,
                                   data=data,
                                   timeout=3) as resp:
            res = await resp
    except Exception as e:
        print(e)
    else:
        if return_type == 'json':
            return res.json()
        else:
            return res.text()
