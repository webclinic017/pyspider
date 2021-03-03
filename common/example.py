import os
import sys

sys.path.append(os.path.abspath(".."))
from common.spider import AsyncSpider


class ExampleSpider(AsyncSpider):
    proxy = "pinzan"
    concurrency = 16
    retry_time = 3
    key = "test"
    redis_env = "aio_test"
    # topic = "test_kafka"
    # kafka_env = "test"
    logger_name = "example_spider"

    default_headers = {
        "authority": "ec.snssdk.com",
        "accept": "application/json, text/plain, */*",
        "origin": "https://haohuo.jinritemai.com",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://haohuo.jinritemai.com/",
        "accept-language": "zh-CN,zh;q=0.9",
    }

    async def start_requests(self):
        shop_list = [
            "aDpceDB",
            "JIBMdzz",
            "QqkdRkd",
            "JlLHLNH",
            "wxATQZg",
            "zYfkZcb",
            "hxiESSw",
            "lVKMfKy",
            "qIvUBNX",
            "PAZfwKy",
        ]
        for shop_id in shop_list[:]:
            meta = {"page": 1, "shop_id": shop_id}
            url = f"https://ec.snssdk.com/shop/goodsList?shop_id={meta['shop_id']}&size=10&page={meta['page']}&b_type_new=0&device_id=0&is_outside=1"
            yield self.Request(
                url,
                callback=self.parse,
                meta=meta,
            )

    def parse(self, res):
        r = res.json()["data"]["list"]
        print(res.json())
        meta = res.meta
        if r:
            yield res.json()
            meta["page"] += 1
            url = f"https://ec.snssdk.com/shop/goodsList?shop_id={meta['shop_id']}&size=10&page={meta['page']}&b_type_new=0&device_id=0&is_outside=1"
            yield res.follow(url, meta=meta)


ExampleSpider.start()
