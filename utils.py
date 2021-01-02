import redis


class RedisClient():
    def __init__(self, env='test') -> None:
        self.db = self.setup_redis(env=env)

    @staticmethod
    def _setup_redis(host='localhost', port=6379, db=0, password=None):
        """连接redis"""
        try:
            pool = redis.ConnectionPool(host=host,
                                        port=port,
                                        db=db,
                                        password=password,
                                        decode_responses=True)
            client = redis.Redis(connection_pool=pool)
        except Exception as e:
            raise e
        else:
            return client

    def setup_redis(self, env='test'):
        if env == 'prod':
            return self._setup_redis(host="172.16.16.15",
                                     port=6379,
                                     password="20A3NBVJnWZtNzxumYOz",
                                     db=1)
        else:
            return self._setup_redis()

    def set_cache(self, name, key, value, cache_cycle=7, refresh=False):
        self.db.hset(name, key, value)
        if self.db.ttl(name) <= 0 or refresh:
            self.db.expire(name, cache_cycle)

    def get_cache(self, name, key):
        cache = self.db.hget(name, key)
        return cache

    def cache(self,
              name,
              key,
              value,
              cache_cycle=7 * 24 * 3600,
              refresh=False):
        cache_data = self.get_cache(name, key)
        if not cache_data:
            self.set_cache(name,
                           key,
                           value,
                           cache_cycle=cache_cycle,
                           refresh=refresh)
            return value
        return cache_data


if __name__ == "__main__":
    r = RedisClient()
    r.set_cache('test1', 'key', 1, cache_cycle=20, refresh=True)
