import random


class Settings:
    retry_time = 3
    concurrency = 20
    delay = random.uniform(0, 1)
    proxy = "pinzan"
    ua_type = "mobile"
    # 消费者数量
    worker_numbers = 4
    timeout = 5
    failed_counts = 0
    success_counts = 0
    key = None
    topic = None
    default_ua = {
        "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "web": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
    }
    default_headers = {
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": " keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
    }
