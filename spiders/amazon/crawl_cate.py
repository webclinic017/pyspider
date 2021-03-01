import sys

if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/spider/pyspider"
sys.path.append(path)
from common.spider import AsyncSpider


class CrawlCategory(AsyncSpider):
    ua_type = "web"
    logger_name = "amazon_category"

    async def start_requests(self):
        url = "https://www.amazon.com/-/zh/gp/site-directory?ref_=nav_em__fullstore_0_1_1_34"
        yield self.Request(url, callback=self.parse)

    def parse(self, response):
        print(response.text)
        assert "手工艺" in response.text


CrawlCategory.start()
