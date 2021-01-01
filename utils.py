from redis import Redis
import redis


class RedisConf(Redis):
    def __init__(self, env='test') -> None:
        # super().__init__()
        self.redis_client = self.setup_redis(env=env)

    def _setup_redis(self, host='localhost', port=6379, db=0, password=None):
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
        if env == 'product':
            return self._setup_redis(host="172.16.16.15",
                                     port=6379,
                                     password="20A3NBVJnWZtNzxumYOz",
                                     db=1)
        else:
            return self._setup_redis()

    def set_cache(self, name, key, value, cache_cycle=7):
        self.hset(name, key, value)
        if self.ttl(name) <= 0:
            self.expire(name, cache_cycle * 24 * 3600)


if __name__ == "__main__":
    r = RedisConf()
