import asyncio
from json.decoder import JSONDecodeError
import logging
import random
import sys
from concurrent.futures import ThreadPoolExecutor
import ujson

import aiohttp
from aiohttp import ClientSession
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class AsyncSpider:
    """异步爬虫，支持异步上下文管理器
    """
    def __init__(self, retry_time=3, concurrency=20, logger=None) -> None:
        self.session = ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.retry_time = retry_time
        self.sem = asyncio.Semaphore(concurrency)
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.request_queue = asyncio.Queue()
        self.request_body_list = {}
        self.executor = ThreadPoolExecutor()

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
            self.logger.error(f"获取ua出错：{e}")

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
                async with self.session.request('GET', url) as res:
                    result = await res.json()
            except Exception as e:
                self.logger.error(e)
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
                     params=None,
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
        async with self.sem:
            try:
                async with self.session.request(method,
                                                url,
                                                headers=headers,
                                                proxy=proxy,
                                                data=data,
                                                params=params,
                                                timeout=timeout) as resp:
                    await asyncio.sleep(delay)
                    res = await resp.text()
            except Exception as e:
                self.logger.error(f'请求{url}出错:{e}')
            else:
                if return_type == 'json':
                    try:
                        return ujson.loads(res)
                    except JSONDecodeError as e:
                        self.logger.error(e)
                return res

    async def crawl(self,
                    url,
                    headers=None,
                    method='GET',
                    data=None,
                    params=None,
                    proxy_type='liebaoV1',
                    ua_type='mobile',
                    return_type='json',
                    timeout=5):
        ua = await self.get_ua(ua_type=ua_type)
        if not headers:
            headers = {}
        if ua:
            headers['User-Agent'] = ua
        else:
            self.logger.warning(
                "can't get available random ua,will use the defult!")
        for _ in range(self.retry_time):
            proxy = await self.get_proxy(proxy_type=proxy_type)
            if proxy:
                res = await self._crawl(url,
                                        method=method,
                                        headers=headers,
                                        proxy=proxy,
                                        data=data,
                                        params=params,
                                        return_type=return_type,
                                        timeout=timeout)
                if res:
                    return res
            else:
                self.logger.error("can't get proxy!")

    async def multiple_request(self, **kwargs):
        result = await asyncio.gather(*[
            asyncio.create_task(self.crawl(url, **kwargs)) for url in range(10)
        ])
        return result

    async def request_worker(self):
        while True:
            request_item = await self.request_queue.get()
            self.worker_tasks.append(request_item)
            if self.request_queue.empty():
                results = await asyncio.gather(*self.worker_tasks,
                                               return_exceptions=True)
                print(results)
                self.worker_tasks = []
                return results
            self.request_queue.task_done()

    async def request_producer(self):
        for url, request_body in self.request_body_list.items():
            task = asyncio.create_task(self.crawl(url, **request_body))
            self.request_queue.put_nowait(task)

    # @staticmethod
    # async def cancel_all_tasks():
    #     """
    #     Cancel all tasks
    #     :return:
    #     """
    #     tasks = []
    #     for task in asyncio.Task.all_tasks():
    #         if task is not asyncio.tasks.Task.current_task():
    #             tasks.append(task)
    #             task.cancel()
    #     await asyncio.gather(*tasks, return_exceptions=True)

    async def close(self):
        if self.session:
            await self.session.close()
        if self.executor:
            self.executor.shutdown()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
