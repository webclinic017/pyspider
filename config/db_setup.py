import json
from json.decoder import JSONDecodeError

import redis
import sys
import pymysql
sys.path.append('..')
from config.db_config import REDIS_CONF


class RedisClient():
    def __init__(self, env='test') -> None:
        self.db = self.setup_redis(env=env)

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
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        self.db.hset(name, key, value)
        if self.db.ttl(name) <= 0 or refresh:
            self.db.expire(name, cache_cycle)

    def get_cache(self, name, key):
        cache = self.db.hget(name, key)
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
    pass


if __name__ == "__main__":
    r = RedisClient()
    r.set_cache('test1', 'key', 1, cache_cycle=20, refresh=True)
