import asyncio
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from inspect import isasyncgen, isgenerator
from types import AsyncGeneratorType
from typing import Any, Awaitable, Dict, NamedTuple

import aiohttp
import async_timeout
import loguru
import ujson
from aiohttp import ClientSession
from config import KafkaClient, RedisClient
from utils.tools import LazyProperty

from common.request import aiorequest
from common.settings import Settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


class RequestBody(NamedTuple):
    url: str
    method: str = "GET"
    headers: Dict[str, Any] = {}
    params: Any = None
    data: Any = None
    callback: Any = None


class AsyncSpider(Settings):
    """异步爬虫，支持异步上下文管理器"""

    def __init__(self, logger=None) -> None:
        self.session = ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.sem = asyncio.Semaphore(self.concurrency)
        self.logger = logger or loguru.logger
        self.request_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor()
        self.Request = RequestBody
        self.loop = asyncio.get_event_loop()
        # self.env = env
        if self.redis_env:
            self.redis_client = RedisClient(self.redis_env)
        if self.kafka_env:
            self.kafka_client = KafkaClient(self.kafka_env)

    # @LazyProperty
    # def redis_client(self):
    #     self._redis_client = RedisClient(self.env)
    #     self.logger.info(f'initialing {repr(self._redis_client)} success!')
    #     return self._redis_client

    async def get_ua(self, ua_type="mobile"):
        random_ua_links = [
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomIosUa",
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomAndroidUa",
        ]
        url = random.choice(random_ua_links)
        if ua_type == "web":
            url = "http://ycrawl.91cyt.com/api/v1/pdd/common/randomUa"
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.get(url) as resp:
                    res = await resp.json()
            ua = res["data"]
            return ua
        except Exception as e:
            self.logger.warning(f"获取ua出错：{repr(e)},将使用默认ua")
            return self.default_ua[self.ua_type]

    async def get_proxy(self, proxy_type="pinzan"):
        assert proxy_type in {"pinzan", "dubsix", "2808", "liebaoV1", ""}
        if not proxy_type:
            return ""
        url = "http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1".format(
            proxy_type
        )
        for _ in range(self.retry_time):
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.request("GET", url) as res:
                        result = await res.json()
            except Exception as e:
                self.logger.error(f"获取代理出错：{repr(e)}")
            else:
                proxy = result.get("data")
                if proxy:
                    return "http://" + proxy

    async def request(
        self,
        url,
        headers=None,
        method="GET",
        data=None,
        params=None,
        callback=None,
        meta=None,
    ):
        if not headers:
            headers = self.default_headers
            ua = await self.get_ua(ua_type=self.ua_type)
            headers["User-Agent"] = ua
        for _ in range(self.retry_time):
            proxy = await self.get_proxy(proxy_type=self.proxy)
            if proxy or proxy == "":
                async with self.sem:
                    res = await aiorequest(
                        url,
                        method=method,
                        headers=headers,
                        proxy=proxy,
                        data=data,
                        params=params,
                        timeout=self.timeout,
                        session=self.session,
                        logger=self.logger,
                        meta=meta,
                    )
                    await asyncio.sleep(self.delay)
                    if not res:
                        self.failed_counts += 1
                    else:
                        self.success_counts += 1
                        result = None
                        if callable(callback):
                            result = callback(res)
                        return result, res
            else:
                self.logger.error("can't get proxy!")

    async def process_callback(self, callback_results, response=None):
        try:
            if isasyncgen(callback_results):
                async for callback_result in callback_results:
                    await self._process_callback(callback_result)
            elif isgenerator(callback_results):
                for callback_result in callback_results:
                    await self._process_callback(callback_result)
        except Exception as e:
            self.logger.exception(e)

    async def _process_callback(self, callback_result):
        if isinstance(callback_result, AsyncGeneratorType):
            await self.process_callback(callback_result)
        elif isinstance(callback_result, RequestBody):
            self.request_queue.put_nowait(self.create_task(callback_result))
        elif isinstance(callback_result, (dict, str)):
            # Process target item
            await self.run_in_executor(self.process_item, callback_result)

    def parse(self, response):
        """
        解析response
        """
        return response.json()

    def process_item(self, result):
        """
        保存数据操作
        """
        if self.key:
            self.redis_client.lpush(
                self.key,
                ujson.dumps(result, ensure_ascii=False),
            )
        if self.topic:
            self.kafka_client.produce(self.topic, value=result)

    async def request_worker(self, is_gather=True):
        worker_tasks = []
        while True:
            request_item = await self.request_queue.get()
            # if not request_item:
            #     self.request_queue.task_done()
            #     return
            if isinstance(request_item, Awaitable):
                if not is_gather:
                    result, res = await request_item
                    await self.process_callback(result, res)
                else:
                    worker_tasks.append(request_item)
                    if self.request_queue.empty():
                        results = await asyncio.gather(
                            *worker_tasks,
                            return_exceptions=True,
                        )
                        worker_tasks = []
                        for result in results:
                            if not isinstance(result, RuntimeError) and result:
                                callback_results, response = result
                                await self.process_callback(callback_results, response)
            else:
                if isinstance(request_item, (dict, str)):
                    await self.run_in_executor(self.process_item, request_item)
            self.request_queue.task_done()

    async def run_in_executor(self, func, *args):
        await self.loop.run_in_executor(self.executor, func, *args)

    def create_task(self, request_body):
        task = asyncio.ensure_future(self.request(**request_body._asdict()))
        return task

    async def request_producer(self):
        async for request_body in self.start_requests():
            task = None
            if isinstance(request_body, RequestBody):
                task = self.create_task(request_body)
            elif isinstance(request_body, (dict, str)) or request_body is None:
                task = request_body
            await self.request_queue.put(task)
        # for _ in range(self.worker_numbers):
        #     await self.request_queue.put(None)

    async def start_requests(self):
        yield self.Request("https://pyhton.org")

    async def run(self):
        consumers = [
            asyncio.ensure_future(self.request_worker())
            for _ in range(self.worker_numbers)
        ]
        for i, worker in enumerate(consumers):
            self.logger.info(f"Worker{i} started: {id(worker)}")
        await self.request_producer()
        await self.request_queue.join()
        # await asyncio.wait(consumers)
        # for worker in consumers:
        #     worker.cancel()
        # await asyncio.gather(*consumers, return_exceptions=True)
        await self.stop()

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
                f"Total requests: {self.failed_counts + self.success_counts}"
            )

            if self.failed_counts:
                self.logger.info(f"Failed requests: {self.failed_counts}")
            self.logger.info(f"Time usage: {end_time - start_time}")
            self.logger.info("Spider finished!")

    @classmethod
    def start(cls, logger=None, loop=None, close_event_loop=True):
        spider = cls(logger=logger)
        # if sys.version_info > (3, 6):
        #     asyncio.run(spider._start())
        # else:
        loop = loop or asyncio.get_event_loop()
        loop.run_until_complete(spider._start())
        if close_event_loop:
            loop.close()
        return spider

    @staticmethod
    async def cancel_all_tasks():
        """
        Cancel all tasks
        """
        tasks = []
        for task in asyncio.Task.all_tasks():
            if task is not asyncio.tasks.Task.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self, _signal=None):
        """
        Finish all running tasks, cancel remaining tasks.
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
