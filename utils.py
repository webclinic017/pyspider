import logging
import logging.handlers
import os
import random

import aiohttp
import redis


def get_logger(file_name):
    """获取日志记录器

    Args:
        file_name (str): [记录日志的文件名]

    Returns:
        [obj]: [logger对象]
    """
    logger = logging.getLogger(__name__)
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


logger = get_logger('utils')


async def get_proxy(self, platform='2808'):
    """获取代理

    Args:
        platform (str, optional): [使用的代理平台]. Defaults to '2808'.

    Returns:
        [str]: [proxy]
    """
    if platform == 'zhilian':
        return 'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
    url = 'http://yproxy.91cyt.com/api/proxyHandler/getProxy/?platform={}&wantType=1'.format(
        platform)
    try:
        async with aiohttp.ClientSession() as ssesion:
            async with ssesion.request('GET', url) as res:
                result = await res.json()
    except Exception as e:
        logger.exception(str(e))
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
        logger.exception("connect redis failed,msg={}".format(e))
        return None
    return client


async def get_ua(platform='mobile'):
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res = await resp.json()
        ua = res['data']
        return ua
    except Exception as e:
        logger.exception(str(e))
        return False
