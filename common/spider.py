import asyncio
from json.decoder import JSONDecodeError
import logging
import random
import ujson

import aiohttp
from aiohttp import ClientSession
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class AsyncSpider():
    """异步爬虫，支持异步上下文管理器
    """
    def __init__(self, retry_time=3, concurrency=20) -> None:
        self.session = ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.retry_time = retry_time
        self.sem = asyncio.Semaphore(concurrency)

    async def get_ua(self, ua_type="mobile"):
        random_ua_links = [
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomIosUa",
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomAndroidUa",
        ]
        url = random.choice(random_ua_links)
        if ua_type == 'web':
            url = "http://ycrawl.91cyt.com/api/v1/pdd/common/randomUa"
        try:
            resp = await self.session.get(url)
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
        assert proxy_type in {'2808', 'dubsix', 'liebao', 'liebaoV1'}
        url = 'http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1'.format(
            proxy_type)
        for _ in range(self.retry_time):
            try:
                res = await self.session.request('GET', url)
                result = await res.json()
            except Exception as e:
                logging.error(e)
            else:
                proxy = result.get('data')
                if proxy:
                    return 'http://' + proxy

    async def _crawl(self,
                     url,
                     method='GET',
                     headers=None,
                     proxy=None,
                     data=None,
                     timeout=5,
                     return_type='json',
                     delay=1):
        """抓取url

        Args:
            url (str): 目标url.
            method (str, optional): 请求方式. Defaults to 'GET'.
            headers (dict, optional): 请求头. Defaults to None.
            proxy (str), optional): 代理. Defaults to None.
            data (str, optional): 请求体. Defaults to None.
            timeout (int, optional): 超时. Defaults to 5.
            return_type (str, optional): 返回数据类型. Defaults to 'json'.
            delay (float|int, optional): 延时下载时间. Defaults to 0.1.

        Returns:
            str: 响应内容
        """
        for _ in range(self.retry_time - 1):
            async with self.sem:
                try:
                    async with self.session.request(method,
                                                    url,
                                                    headers=headers,
                                                    proxy=proxy,
                                                    data=data,
                                                    timeout=timeout) as resp:
                        await asyncio.sleep(delay)
                        res = await resp.text()
                except Exception as e:
                    logging.error(e)
                else:
                    if return_type == 'json':
                        try:
                            return ujson.loads(res)
                        except JSONDecodeError as e:
                            logging.error(e)
                    return res

    async def crawl(self,
                    url,
                    headers=None,
                    method='GET',
                    data=None,
                    proxy_type='liebaoV1',
                    ua_type='mobile',
                    return_type='json',
                    timeout=5):
        proxy = await self.get_proxy(proxy_type=proxy_type)
        ua = await self.get_ua(ua_type=ua_type)
        if not headers:
            headers = {}
        if ua:
            headers['User-Agent'] = ua
        else:
            logging.warning(
                "can't get available random ua,will use the defult!")
        if proxy:
            res = await self._crawl(url,
                                    method=method,
                                    headers=headers,
                                    proxy=proxy,
                                    data=data,
                                    return_type=return_type,
                                    timeout=timeout)
            return res
        else:
            raise Exception("can't get proxy!")

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
