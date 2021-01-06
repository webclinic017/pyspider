import json
from json.decoder import JSONDecodeError
import logging

import redis
import sys
import pymysql
sys.path.append('..')
from config.db_config import REDIS_CONF, MYSQL_CONF


class RedisClient(redis.Redis):
    def __init__(self, env='test') -> None:
        self.pool = redis.ConnectionPool(**REDIS_CONF[env])
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


if __name__ == "__main__":
    r = RedisClient()
    r.set_cache('test1', 'key', 1, cache_cycle=20, refresh=True)
    m = MysqlClient()
    # m.create_table()
    # m.insert_data()
    m.close()
