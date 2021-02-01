import json
import sys
sys.path.append('C:\\Users\\Ety\\Desktop\\pyspider')
from common.spider import AsyncSpider
from utils.log import get_logger

logger = get_logger('example_spider')


class ExampleSpider(AsyncSpider):
    proxy = 'liebaoV1'
    worker_numbers = 4
    concurrency = 16

    def __init__(self, logger=None) -> None:
        super().__init__(logger=logger)
        # print(self.__class__.proxy)

    @staticmethod
    def make_headers():
        headers = {
            'authority': 'ec.snssdk.com',
            'accept': 'application/json, text/plain, */*',
            'user-agent':
            'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
            'origin': 'https://haohuo.jinritemai.com',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://haohuo.jinritemai.com/',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        return headers

    async def make_request_body(self):
        shop_list = [
            'aDpceDB', 'JIBMdzz', 'QqkdRkd', 'JlLHLNH', 'wxATQZg', 'zYfkZcb',
            'zYfkZcb', 'hxiESSw', 'lVKMfKy', 'qIvUBNX', 'PAZfwKy'
        ]
        for shop_id in shop_list:
            for page in range(10):
                url = f'https://ec.snssdk.com/shop/goodsList?shop_id={shop_id}&size=10&page={page}&b_type_new=0&device_id=0&is_outside=1'
                method = 'GET'
                headers = self.make_headers()
                yield self.RequestBody(url, method, headers)

    def parse(self, res):
        logger.info(res)
        # self.redis_client.lpush('mytest', json.dumps(res))


ExampleSpider.start(logger=logger)
