import asyncio
import sys
sys.path.append('..')
from common.spider import AsyncSpider


async def fetch_page():
    async with AsyncSpider() as spider:
        res = await spider.crawl("https://www.baidu.com",
                                 return_type='text',
                                 proxy_type='liebaoV1')
        return res


def test_async_spider():
    res = asyncio.run(fetch_page())
    # print(res)
    assert res is not None


if __name__ == "__main__":
    test_async_spider()
