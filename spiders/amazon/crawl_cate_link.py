import sys


if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/spider/pyspider"
sys.path.append(path)
from common.spider import AsyncSpider
from common.response import Response
from constants.redis_key import Amazon


class CrawlCategory(AsyncSpider):
    ua_type = "web"
    logger_name = "amazon_category"
    domain = "https://www.amazon.com"
    timeout = 10
    redis_env = "aio_redis30"
    redis_db = 3

    headers = {
        "authority": "www.amazon.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "rtt": "700",
        "downlink": "1.4",
        "ect": "3g",
        "upgrade-insecure-requests": "1",
        # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": 'session-id=135-5352300-7328512; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466; i18n-prefs=USD; session-id-time=2082787201l; s_vnum=2046595639287%26vn%3D1; s_nr=1614595643430-New; s_dslv=1614595643432; session-token=O9fWSvtXPqA/wBReFTtjYU9VdK4AGm6SjfxYvnOvGG3jRodos/h+oXdjiVhCuHDffmiRD7kqnPrkHtpqecv8cZdtcs151ZJvZPIxpXO4bNVlO+VbiAt7RhBTs3RYreD30d5gqE9bvW0OIHBfoA3PyI+S0TQti8vuB94IvSPmgL9gpPTCVG35Rx6fW46mXDFL; csm-hit=tb:PZQKF4HWGNP7JA68QEAR+s-PZQKF4HWGNP7JA68QEAR|1614651991243&t:1614651991243&adb:adblk_no; lc-main=zh_CN; session-id=135-5352300-7328512; session-id-time=2082787201l; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466',
    }

    async def start_requests(self):
        url = "https://www.amazon.com/-/zh/gp/site-directory?ref_=nav_em__fullstore_0_1_1_34"
        yield self.Request(url, headers=self.headers, callback=self.parse)

    async def parse(self, response: Response):
        cate_data = {}
        bs = response.html_tree()
        a = bs.find_all("a", {"class": "a-link-normal fsdLink fsdDeptLink"})
        for cate in a:
            cate_data["cate_name"] = cate.get_text().strip()
            link = self.domain + cate.get("href").strip()
            await self.redis_client.sadd(Amazon.CATE_LINK_SET, link)
            cate_data["link"] = link
            print(cate_data)
            yield response.follow(link, callback=self.parse_second_cate)

    async def parse_second_cate(self, res: Response):
        bs = res.html_tree()
        data = bs.find_all("a", {"class": "a-link-normal s-navigation-item"})
        if data:
            for cate in data:
                text = cate.get_text().strip()
                link = self.domain + cate.get("href").strip()
                await self.redis_client.sadd(Amazon.CATE_LINK_SET, link)
                print(f"{text}:{link}")
                yield res.follow(link)


CrawlCategory.start()
