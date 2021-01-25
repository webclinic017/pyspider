import sys
sys.path.append('..')
from common.spider import AsyncSpider
from utils.log import get_logger

logger = get_logger('example_spider')


class ExampleSpider(AsyncSpider):
    proxy = 'liebaoV1'

    def __init__(self, logger=None) -> None:
        super().__init__(logger=logger)
        # print(self.__class__.proxy)

    @staticmethod
    def make_headers(page):
        headers = {
            'authority': 'xiapi.xiapibuy.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'x-shopee-language': 'zh-Hant',
            'x-requested-with': 'XMLHttpRequest',
            'if-none-match-': '55b03-4708e5c11537a4f446e46b7d5513e1c6',
            'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'x-api-source': 'pc',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer':
            f'https://xiapi.xiapibuy.com/search?keyword=%E6%87%B6%E4%BA%BA%E6%B2%99%E7%99%BC&page={page}',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        return headers

    async def make_request_body(self):
        for page in range(1, 100):
            url = f'https://xiapi.xiapibuy.com/api/v2/search_items/?by=relevancy&keyword=%E6%87%B6%E4%BA%BA%E6%B2%99%E7%99%BC&limit=50&newest={int(page-1)* 50}&order=desc&page_type=search&version=2'
            method = 'GET'
            headers = self.make_headers(page)
            request_body = self.RequestBody(url, method, headers)
            # self.request_body_list.append(request_body)
            yield request_body

    def process_response(self, res):
        self.logger.info(type(res))


async def main():
    async with ExampleSpider() as spider:
        await spider._start()


# asyncio.run(main())
ExampleSpider.start(logger=logger)
