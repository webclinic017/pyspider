import pybreaker
import redis
# from tenacity import retry
# from tenacity.stop import stop_after_attempt
# from tenacity.wait import wait_random

RETRY_TIME = 3
breaker = pybreaker.CircuitBreaker(fail_max=10)


def init_redis_client(host='localhost', port=6379, password=None, db=0):
    """连接redis"""
    try:
        pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    db=db,
                                    password=password,
                                    decode_responses=True)
        client = redis.Redis(connection_pool=pool)
    except Exception as e:
        print(e)
    else:
        return client
