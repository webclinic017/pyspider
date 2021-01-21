import asyncio
import sys
sys.path.append('..')
from common.spider import AsyncSpider


class ExampleSpider(AsyncSpider):
    def __init__(self, logger=None) -> None:
        super().__init__(logger=logger)

    @staticmethod
    def make_headers():
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
            'https://xiapi.xiapibuy.com/search?keyword=%E6%87%B6%E4%BA%BA%E6%B2%99%E7%99%BC&page=1',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        return headers

    async def make_request_body(self):
        for page in range(1, 100):
            request_body = {}
            request_body[
                'url'] = f'https://xiapi.xiapibuy.com/api/v2/search_items/?by=relevancy&keyword=%E6%87%B6%E4%BA%BA%E6%B2%99%E7%99%BC&limit=50&newest={int(page-1)* 50}&order=desc&page_type=search&version=2'
            request_body['method'] = 'GET'
            request_body['headers'] = self.make_headers()
            self.request_body_list.append(request_body)

    # async def run(self):
    #     self.make_request_body()
    #     await self.request_producer()
    #     await self.request_worker()


async def main():
    async with ExampleSpider() as spider:
        await spider.run()


asyncio.run(main())
