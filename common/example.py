import random
import sys
sys.path.append('C:\\Users\\Ety\\Desktop\\my_spider')
from common.spider import AsyncSpider
from utils.log import get_logger

logger = get_logger('example_spider')


class ExampleSpider(AsyncSpider):
    proxy = 'liebaoV1'
    worker_numbers = 3
    delay = random.uniform(0, 1)
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
        page = 1
        shop_list = [
            'aDpceDB', 'JIBMdzz', 'QqkdRkd', 'JlLHLNH', 'wxATQZg', 'zYfkZcb',
            'zYfkZcb', 'hxiESSw', 'lVKMfKy', 'qIvUBNX', 'PAZfwKy'
        ]
        for shop_id in shop_list:
            for page in range(30):
                url = f'https://ec.snssdk.com/shop/goodsList?shop_id={shop_id}&size=10&page={page}&b_type_new=0&device_id=0&is_outside=1'
                method = 'GET'
                headers = self.make_headers()
                yield self.RequestBody(url, method, headers)
                # if isinstance(res, dict):
                #     if res['data'].get('list'):
                #         page += 1
                #     else:
                #         break

    def parse(self, res):
        logger.info((res))


# async def main():
#     async with ExampleSpider() as spider:
#         await spider._start()

# asyncio.run(main())
ExampleSpider.start(logger=logger)
