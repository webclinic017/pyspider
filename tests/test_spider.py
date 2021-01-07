import asyncio
import sys
import os
sys.path.append(os.pardir)
from common.spider import AsyncSpider
from config.db_setup import RedisClient


async def fetch_page():
    async with AsyncSpider() as spider:
        res = await spider.crawl("http://www.baidu.com",
                                 return_type='text',
                                 proxy_type='liebaoV1')
        return res


def test_async_spider():
    res = asyncio.run(fetch_page())
    # print(res)
    assert res is not None


def test_redis_client():
    redis_client = RedisClient()
    new_var = 'pytest'
    cache_cycle = 60
    redis_client.set_cache(new_var,
                           'test',
                           'test_pytest',
                           cache_cycle=60,
                           refresh=True)
    assert redis_client.exists(new_var) == 1
    assert redis_client.ttl(new_var) == cache_cycle


if __name__ == "__main__":
    test_async_spider()
