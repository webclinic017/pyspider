redis_test = {
    'host': 'localhost',
    'port': 6379,
    'password': None,
    'db': 0,
    'decode_responses': True
}

redis_15 = {
    'host': '172.16.16.15',
    'port': 6379,
    'password': '20A3NBVJnWZtNzxumYOz',
    'db': 1,
    'decode_responses': True
}
aioredis_test = {
    'address': ('localhost', 6379),
    'password': None,
    'db': 0,
    'encoding': 'utf-8'
}

aioredis_15 = {
    'address': ('172.16.16.15', 6379),
    'password': '20A3NBVJnWZtNzxumYOz',
    'db': 1,
    'encoding': 'utf-8'
}

mysql_test = {
    'host': 'localhost',
    'port': 3306,
    'user': 'wangxin',
    'password': '965213',
    'db': 'mysql'
}

REDIS_CONF = {
    'test': redis_test,
    'redis15': redis_15,
    'aio_test': aioredis_test,
    'aio_redis15': aioredis_15
}

MYSQL_CONF = {'test': mysql_test}
