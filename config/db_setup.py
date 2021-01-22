import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from json.decoder import JSONDecodeError

import aiomysql
import aioredis
import kafka
import pymysql
import redis

sys.path.append('..')
from config.db_config import KAFKA_CONF, MYSQL_CONF, REDIS_CONF


class RedisClient(redis.Redis):
    def __init__(self, env='test', db=0) -> None:
        self.pool = redis.ConnectionPool(db=db, **REDIS_CONF[env])
        super().__init__(connection_pool=self.pool)
        # self.db = self.setup_redis(env=env)

    @staticmethod
    def _setup_redis(**kwargs):
        """连接redis"""
        try:
            pool = redis.ConnectionPool(**kwargs)
            client = redis.Redis(connection_pool=pool)
        except Exception as e:
            raise e
        else:
            return client

    def setup_redis(self, env='test'):
        return self._setup_redis(**REDIS_CONF[env])

    def set_cache(self, name, key, value, cache_cycle=7, refresh=False):
        """
        设置键的生存时间
        """
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        self.hset(name, key, value)
        if self.ttl(name) <= 0 or refresh:
            self.expire(name, cache_cycle)

    def get_cache(self, name, key):
        cache = self.hget(name, key)
        if cache:
            try:
                cache = json.loads(cache)
            except JSONDecodeError as e:
                print(e)
        return cache

    def cache(self, name, key, value, cache_cycle=1000, refresh=False):
        cache_data = self.get_cache(name, key)
        if not cache_data:
            self.set_cache(name,
                           key,
                           value,
                           cache_cycle=cache_cycle,
                           refresh=refresh)
            return value
        return cache_data


class MysqlClient:
    def __init__(self, env='test') -> None:
        self.conn = self.setup_connection(env=env)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    @staticmethod
    def _setup_connection(**kwargs):
        try:
            conn = pymysql.connect(**kwargs)
        except pymysql.Error as e:
            logging.error(f'数据库连接失败:{e}')
            raise
        return conn

    def setup_connection(self, env='test'):
        return self._setup_connection(**MYSQL_CONF[env])

    def create_table(self, sql):
        # sql = "CREATE TABLE if not exists birds (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),description TEXT)"
        self.cursor.execute(sql)
        return True

    def insert_data(self, sql):
        # sql = "INSERT INTO birds (name,description) VALUES ('alix minor','wood duck')"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except pymysql.err.OperationalError as e:
            logging.error(e)
            self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class AioRedis:
    def __init__(self, env='aio_test') -> None:
        self.env = env

    async def setup(self):
        try:
            aioredis_client = await aioredis.create_redis_pool(
                **REDIS_CONF[self.env])
        except Exception as e:
            raise Exception(f'异步redis连接失败:{e}')
        return aioredis_client

    async def close(self):
        client = await self.setup()
        client.close()
        await client.wait_closed()

    async def __aenter__(self):
        return await self.setup()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


@asynccontextmanager
async def aio_mysql(env='test'):
    pool = await aiomysql.create_pool(**MYSQL_CONF[env])
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                yield cur
            except Exception as e:
                logging.error(e)
            finally:
                cur.close()
    pool.close()
    await pool.wait_closed()


class AioMysql:
    def __init__(self, env='test') -> None:
        self.env = env
        self.conn = None
        self.cursor = None

    async def setup(self):
        self.pool = await aiomysql.create_pool(**MYSQL_CONF[self.env])
        self.conn = await self.pool.acquire()
        self.cursor = await self.conn.cursor()

    async def create_table(self, sql):
        await self.cursor.execute(sql)
        return True

    async def close(self):
        if self.cursor:
            await self.cursor.close()
        # if self.conn:
        #     await self.conn.close()
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


class KafkaClient:
    def __init__(self, env='test', logger=None) -> None:
        self.env = env
        self.producer = kafka.KafkaProducer(**KAFKA_CONF[self.env])
        self.consumer = kafka.KafkaConsumer(**KAFKA_CONF[self.env])
        if not logger:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    def produce(self, topic, value, key=None):
        self.producer.send(topic, value, key=key).add_callback(
            self.on_send_success).add_errback(self.on_send_error)

    def consume(self, *topics, group_id=None):
        self.consumer.subscribe(topics)
        if group_id:
            self.consumer.config['group_id'] = group_id
        for msg in self.consumer:
            self.consumer.poll(0)
            print(msg.value)
            yield msg.value

    def on_send_success(self, record_metadata):
        self.logger.info('Message delivered to {} [{}]'.format(
            record_metadata.topic, record_metadata.partition))

    def on_send_error(self, exc):
        self.logger.error('I am an errback', exc_info=exc)


async def conn_aiomysql():
    sql = "CREATE TABLE if not exists test_mysql (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),description TEXT)"
    async with AioMysql() as mysql_client:
        r = await mysql_client.create_table(sql)
    print(r)


if __name__ == "__main__":
    # _r = RedisClient().get('test')
    # print(_r)
    # r = asyncio.run(AioRedis().setup())
    # m = asyncio.run(AioMysql().setup())
    asyncio.run(conn_aiomysql())
