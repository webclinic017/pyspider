import asyncio
import logging
import random
import sys
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Awaitable

import aiohttp
import async_timeout
import ujson
from aiohttp import ClientSession

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

RequestBody = namedtuple('requestBody',
                         ['url', 'method', 'headers', 'params', 'data'],
                         defaults=[None, 'GET', None, None, None])


class AsyncSpider:
    """异步爬虫，支持异步上下文管理器
    """
    retry_time = 3
    concurrency = 20
    delay = random.uniform(0, 1)
    proxy = 'liebaoV1'
    ua_type = 'web'
    # 消费者数量
    worker_numbers = 2
    batch_num = 10
    timeout = 5
    failed_counts = 0
    success_counts = 0

    def __init__(self, logger=None) -> None:
        self.session = ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.sem = asyncio.Semaphore(self.concurrency)
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)
        self.request_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor()
        self.worker_tasks = []
        self.RequestBody = RequestBody
        self.loop = asyncio.get_event_loop()

    async def get_ua(self, ua_type="mobile"):
        random_ua_links = [
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomIosUa",
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomAndroidUa",
        ]
        url = random.choice(random_ua_links)
        if ua_type == 'web':
            url = "http://ycrawl.91cyt.com/api/v1/pdd/common/randomUa"
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.get(url) as resp:
                    res = await resp.json()
            ua = res['data']
            return ua
        except Exception as e:
            self.logger.error(f"获取ua出错：{repr(e)}")

    async def get_proxy(self, proxy_type='pinzan'):
        assert proxy_type in {'pinzan', 'dubsix', '2808', 'liebaoV1', ''}
        if not proxy_type:
            return ''
        url = 'http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1'.format(
            proxy_type)
        for _ in range(self.retry_time):
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.request('GET', url) as res:
                        result = await res.json()
            except Exception as e:
                self.logger.error(f'获取代理出错：{repr(e)}')
            else:
                proxy = result.get('data')
                if proxy:
                    return 'http://' + proxy

    async def _request(self,
                       url,
                       method='GET',
                       headers=None,
                       proxy=None,
                       data=None,
                       params=None,
                       return_type='json'):
        async with self.sem:
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.request(method,
                                                    url,
                                                    headers=headers,
                                                    proxy=proxy,
                                                    data=data,
                                                    params=params) as resp:
                        await asyncio.sleep(self.delay)
                        res = await resp.text()
            except aiohttp.ClientHttpProxyError as e:
                self.logger.error(f'代理出错：{repr(e)}')
            except Exception as e:
                self.logger.error(f'请求{url}出错:{repr(e)}')
            else:
                if return_type == 'json':
                    try:
                        return ujson.loads(res)
                    except JSONDecodeError as e:
                        self.logger.error(e)
                return res

    async def request(self,
                      url=None,
                      headers=None,
                      method='GET',
                      data=None,
                      params=None,
                      return_type='json'):
        if not url:
            raise Exception("url must not be None!")
        ua = await self.get_ua(ua_type=self.ua_type)
        if not headers:
            headers = {}
        if ua:
            headers['User-Agent'] = ua
            if 'user-agent' in headers:
                del headers['user-agent']
        else:
            self.logger.warning(
                "can't get available random ua,will use the defult!")
        for _ in range(self.retry_time):
            proxy = await self.get_proxy(proxy_type=self.proxy)
            if proxy or proxy == '':
                res = await self._request(url,
                                          method=method,
                                          headers=headers,
                                          proxy=proxy,
                                          data=data,
                                          params=params,
                                          return_type=return_type)
                if res:
                    return res
            else:
                self.logger.error("can't get proxy!")

    def parse(self, response):
        """
        解析response
        """
        print(response)

    def process_item(self, item):
        """
        保存数据操作
        """
        pass

    async def request_worker(self, is_gather=True):
        while True:
            request_item = await self.request_queue.get()
            # if not request_item:
            #     self.request_queue.task_done()
            #     return
            if isinstance(request_item, Awaitable):
                if not is_gather:
                    result = await request_item
                    if isinstance(result, (dict, str)):
                        self.success_counts += 1
                        # self.process_response(result)
                        await self.loop.run_in_executor(
                            self.executor, self.parse, result)
                    else:
                        self.failed_counts += 1
                else:
                    self.worker_tasks.append(request_item)
                    if self.request_queue.empty():
                        results = await asyncio.gather(*self.worker_tasks,
                                                       return_exceptions=True)
                        self.worker_tasks = []
                        for result in results:
                            if isinstance(result, (dict, str)):
                                self.success_counts += 1
                                # self.process_response(result)
                                await self.loop.run_in_executor(
                                    self.executor, self.parse, result)
                            else:
                                self.failed_counts += 1
            else:
                if isinstance(request_item, (dict, str)):
                    self.success_counts += 1
                    # self.process_response(result)
                    await self.loop.run_in_executor(self.executor, self.parse,
                                                    request_item)
                else:
                    self.failed_counts += 1

            self.request_queue.task_done()

    async def request_producer(self):
        async for request_body in self.make_request_body():
            task = None
            if isinstance(request_body, RequestBody):
                task = asyncio.ensure_future(
                    self.request(**request_body._asdict()))
            elif isinstance(request_body, (dict, str)) or request_body is None:
                task = request_body
            await self.request_queue.put(task)
        # for _ in range(self.worker_numbers):
        #     await self.request_queue.put(None)
        await self.request_queue.join()

    async def make_request_body(self):
        yield self.RequestBody()

    async def run(self):
        consumers = [
            asyncio.ensure_future(self.request_worker())
            for _ in range(self.worker_numbers)
        ]
        for i, worker in enumerate(consumers):
            self.logger.info(f"Worker{i} started: {id(worker)}")
        await self.request_producer()
        # await asyncio.wait(consumers)
        for worker in consumers:
            worker.cancel()
            # self.logger.info(r)
        await asyncio.gather(*consumers, return_exceptions=True)

    async def _start(self):
        self.logger.info("Spider started!")
        start_time = datetime.now()
        try:
            await self.run()
        finally:
            await self.close()
            # Display logs about this crawl task
            end_time = datetime.now()
            self.logger.info(
                f"Total requests: {self.failed_counts + self.success_counts}")

            if self.failed_counts:
                self.logger.info(f"Failed requests: {self.failed_counts}")
            self.logger.info(f"Time usage: {end_time - start_time}")
            self.logger.info("Spider finished!")

    @classmethod
    def start(cls, logger=None, close_event_loop=True):
        spider = cls(logger=logger)
        # if sys.version_info > (3, 6):
        #     asyncio.run(spider._start())
        # else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(spider._start())
        if close_event_loop:
            loop.close()
        return spider

    @staticmethod
    async def cancel_all_tasks():
        """
        Cancel all tasks
        :return:
        """
        tasks = []
        for task in asyncio.Task.all_tasks():
            if task is not asyncio.tasks.Task.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self, _signal):
        """
        Finish all running tasks, cancel remaining tasks.
        :param _signal:
        :return:
        """
        self.logger.info("Stopping spider")
        await self.cancel_all_tasks()

    async def close(self):
        if self.session:
            await self.session.close()
        if self.executor:
            self.executor.shutdown()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
