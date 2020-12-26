import json
import logging
import logging.handlers
import os
import random

import pybreaker
import redis
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

RETRY_TIME = 3
breaker = pybreaker.CircuitBreaker(fail_max=10)


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


class BasicSpider:
    def __init__(self, session, retry_time=3) -> None:
        self.session = session
        self.retry_time = retry_time

    async def get_ua(self, ua_type="mobile"):
        random_ua_links = [
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomIosUa",
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomAndroidUa",
        ]
        url = random.choice(random_ua_links)
        if ua_type == 'web':
            url = "http://ycrawl.91cyt.com/api/v1/pdd/common/randomUa"
        try:
            async with self.session.get(url) as resp:
                res = await resp.json()
            ua = res['data']
            return ua
        except Exception as e:
            logging.error(f"获取ua出错：{e}")

    async def get_proxy(self, proxy_type='pinzan'):
        """获取代理

        Args:
            proxy_type (str, optional): [使用的代理平台]. Defaults to 'pinzan'.

        Returns:
            [str]: [proxy]
        """
        assert proxy_type in {'zhilian', '2808', 'dubsix', 'liebao'}
        if proxy_type == 'zhilian':
            return 'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
        url = 'http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1'.format(
            proxy_type)
        try:
            async with self.session.request('GET', url) as res:
                result = await res.json()
        except Exception as e:
            logging.error(e)
        else:
            proxy = result.get('data')
            if proxy:
                return 'http://' + proxy

    @breaker
    @retry(stop=stop_after_attempt(RETRY_TIME), wait=wait_random(min=0, max=1))
    async def _crawler(self,
                       url,
                       method='GET',
                       headers=None,
                       proxy=None,
                       data=None,
                       timeout=5,
                       return_type='json'):
        for _ in range(self.retry_time - 1):
            try:
                async with self.session.request(method,
                                                url,
                                                headers=headers,
                                                proxy=proxy,
                                                data=data,
                                                timeout=timeout) as resp:
                    res = await resp.text()
            except Exception as e:
                logging.error(e)
            else:
                if return_type == 'json':
                    return json.loads(res)
                return res

    async def crawler(self,
                      url,
                      method='GET',
                      headers=None,
                      data=None,
                      proxy_type='pinzan',
                      ua_type='mobile',
                      return_type='json',
                      timeout=5):
        proxy = await self.get_proxy(proxy_type=proxy_type)
        ua = await self.get_ua(ua_type=ua_type)
        if ua:
            headers['User-Agent'] = ua
        else:
            logging.warning(
                "can't get avalible random ua,will use the defult!")
        if proxy:
            res = await self._crawler(url,
                                      method=method,
                                      headers=headers,
                                      proxy=proxy,
                                      data=data,
                                      return_type=return_type,
                                      timeout=timeout)
            return res
        else:
            raise Exception("can't get proxy!")
