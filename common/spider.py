import asyncio
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from inspect import isasyncgen, iscoroutinefunction, isgenerator
from types import AsyncGeneratorType
from typing import Awaitable

import async_timeout
import ujson
from aiohttp import ClientSession, TCPConnector
from aioredis import Redis
from config import AioRedis, KafkaClient, RedisClient, TendisClient
from utils.log import get_loguru_logger
from utils.proxy import get_long_proxy

from common.request import aiorequest
from common.response import RequestBody, Response
from common.settings import Settings

# from utils.tools import LazyProperty

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


class AsyncSpider(Settings):
    """异步通用爬虫"""

    start_urls = []

    def __init__(self, session=None) -> None:
        self.session = session or ClientSession(
            connector=TCPConnector(ssl=False), trust_env=True
        )
        self.sem = asyncio.Semaphore(self.concurrency)
        self.request_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor()
        self.Request = RequestBody
        self.loop = asyncio.get_event_loop()
        # self.env = env
        self.logger = get_loguru_logger(self.logger_name)
        self.redis_client = None
        self.aioredis_client = None
        if self.redis_env in ("test", "redis15", "redis30"):
            self.redis_client = RedisClient(self.redis_env, self.redis_db)
        elif self.redis_env == "tendis":
            self.redis_client = TendisClient()
        elif self.redis_env in ("aio_test", "aio_redis15", "aio_redis30"):
            self.aioredis_client = AioRedis(self.redis_env, self.redis_db)

        if self.kafka_env:
            self.kafka_client = KafkaClient(self.kafka_env, self.logger)

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
        assert proxy_type in {"pinzan", "dubsix", "2808", "liebaoV1", "long", ""}
        if not proxy_type:
            return ""
        elif proxy_type == "long":
            return get_long_proxy()
        url = "http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1".format(
            proxy_type
        )
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

    @staticmethod
    async def fetch_callback(callback, res):
        if not callable(callback):
            raise TypeError("callback must be callable!")
        elif iscoroutinefunction(callback):
            result = await callback(res)
        else:
            result = callback(res)
        return result

    async def request(
        self,
        url,
        headers=None,
        method="GET",
        data=None,
        params=None,
        callback=None,
        meta=None,
        **kwargs,
    ):
        if not headers:
            headers = self.default_headers
        if "User-Agent" or "user-agent" not in headers:
            ua = await self.get_ua(ua_type=self.ua_type)
            headers["user-agent"] = ua
        if self.retry_time <= 0:
            self.retry_time = 1
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
                        callback=callback,
                    )
                    await asyncio.sleep(self.delay)
                    if not res:
                        self.failed_counts += 1
                    else:
                        self.success_counts += 1
                        if callback:
                            result = await self.fetch_callback(callback, res)
                            return result
                        else:
                            return res
            else:
                self.logger.error("can't get proxy!")

    async def process_callback(self, callback_results):
        try:
            if isasyncgen(callback_results):
                async for callback_result in callback_results:
                    await self._process_callback(callback_result)
            elif isgenerator(callback_results):
                for callback_result in callback_results:
                    await self._process_callback(callback_result)
            else:
                await self._process_callback(callback_results)
        except Exception as e:
            self.logger.exception(e)

    async def _process_callback(self, callback_result):
        if isinstance(callback_result, AsyncGeneratorType):
            await self.process_callback(callback_result)
        elif isinstance(callback_result, RequestBody):
            self.request_queue.put_nowait(self.create_task(callback_result))
        elif isinstance(callback_result, (dict, str, Response)):
            # Process target item
            # await self.run_in_executor(self.process_item, callback_result)
            await self.process_item(callback_result)

    async def parse(self, response: Response):
        """
        解析response
        """
        return response.text

    async def process_item(self, result):
        """
        保存数据操作
        """
        if isinstance(result, dict):
            data = ujson.dumps(result, ensure_ascii=False)
        elif isinstance(result, Response):
            try:
                data = result.json()
            except Exception:
                self.logger.warning("response is not a json str!")
                data = result.text
        else:
            data = result
        if self.key and self.redis_client:
            if isinstance(self.redis_client, RedisClient):
                self.redis_client.lpush(self.key, data)
            elif isinstance(self.redis_client, Redis):
                await self.redis_client.lpush(self.key, data)
            self.logger.info(f"保存数据到队列{self.key}成功！")
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
                    data = await request_item
                    if data:
                        await self.process_callback(*data)
                else:
                    worker_tasks.append(request_item)
                    if self.request_queue.empty():
                        results = await asyncio.gather(
                            *worker_tasks,
                            return_exceptions=True,
                        )
                        worker_tasks.clear()
                        for result in results:
                            if not isinstance(result, RuntimeError) and result:
                                await self.process_callback(result)
            else:
                if isinstance(request_item, (dict, str)):
                    await self.run_in_executor(self.process_item, request_item)
            self.request_queue.task_done()

    async def run_in_executor(self, func, *args):
        await self.loop.run_in_executor(self.executor, func, *args)

    def create_task(self, request_body):
        task = asyncio.ensure_future(self.request(**request_body._asdict()))
        return task

    async def put_task(self, request_body):
        task = None
        if isinstance(request_body, RequestBody):
            task = self.create_task(request_body)
        elif isinstance(request_body, (dict, str)) or request_body is None:
            task = request_body
        if task:
            await self.request_queue.put(task)

    async def request_producer(self):
        gen = self.start_requests()
        if isasyncgen(gen):
            async for request_body in gen:
                await self.put_task(request_body)
        elif isgenerator(gen):
            for request_body in gen:
                await self.put_task(request_body)
        # for _ in range(self.worker_numbers):
        #     await self.request_queue.put(None)

    def start_requests(self):
        if self.start_urls:
            for url in self.start_urls:
                yield self.Request(url, callback=self.parse)

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
        if self.aioredis_client:
            self.redis_client = await self.aioredis_client.setup()
        try:
            await self.run()
        except Exception as e:
            self.logger.error(e)
        finally:
            await self.close()
        # Display logs about this crawl task
        end_time = datetime.now()
        self.logger.info(f"Total requests: {self.failed_counts + self.success_counts}")
        if self.failed_counts:
            self.logger.info(f"Failed requests: {self.failed_counts}")
        self.logger.info(f"Time usage: {end_time - start_time}")
        self.logger.info("Spider finished!")

    @classmethod
    def start(cls, loop=None, close_event_loop=True):
        spider = cls()
        # if sys.version_info > (3, 6):
        #     asyncio.run(spider._start())
        # else:
        loop = loop or asyncio.get_event_loop()
        loop.run_until_complete(spider._start())
        if close_event_loop:
            loop.close()
        return spider

    @classmethod
    async def async_start(cls, session=None, loop=None):
        loop = loop or asyncio.get_event_loop()
        spider_ins = cls(session)
        await spider_ins._start()

        return spider_ins

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
        if self.aioredis_client:
            await self.aioredis_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
