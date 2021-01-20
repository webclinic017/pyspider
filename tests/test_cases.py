import asyncio
import sys
import os
import pytest
import pytest_asyncio
sys.path.append(os.pardir)
from common.spider import AsyncSpider
from config.db_setup import RedisClient, MysqlClient, AioRedis, AioMysql


async def fetch_page():
    async with AsyncSpider() as spider:
        res = await spider.crawl("https://python.org",
                                 return_type='text',
                                 proxy_type='liebaoV1')
        return res


def test_async_spider():
    res = asyncio.run(fetch_page())
    # print(res)
    assert 'python' in res


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


def test_mysql_client():
    mysql_client = MysqlClient()
    sql = "CREATE TABLE if not exists mytest (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),description TEXT)"
    r = mysql_client.create_table(sql)
    mysql_client.close()
    assert r is True


async def conn_aioredis():
    async with AioRedis() as redis_client:
        await redis_client.set('my_key', 'value')
        return await redis_client.get('my_key')


def test_aioredis():
    r = asyncio.run(conn_aioredis())
    assert r == 'value'


async def conn_aiomysql():
    sql = "CREATE TABLE if not exists pytest (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),description TEXT)"
    async with AioMysql() as mysql_client:
        r = await mysql_client.create_table(sql)
    return r


def test_aiomysql():
    r = asyncio.run(conn_aiomysql())
    assert r == True


if __name__ == "__main__":
    test_async_spider()
