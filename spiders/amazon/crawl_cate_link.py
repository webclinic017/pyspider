import sys


if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/spider/pyspider"
sys.path.append(path)
from common.spider import AsyncSpider
from common.response import Response


class CrawlCategory(AsyncSpider):
    ua_type = "web"
    logger_name = "amazon_category"

    headers = {
        "authority": "www.amazon.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "rtt": "500",
        "downlink": "1.45",
        "ect": "3g",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": 'session-id=135-5352300-7328512; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466; i18n-prefs=USD; skin=noskin; session-id-time=2082787201l; session-token=zT4TgP3/eDFg52yG9QaJVKmwxv1ShSMBzzRzcRfZZEOUNOvVRpyaTO0NlLOUFQedbQmoN4uAIQ2gBUSKym4kWdl4KK1dHynRz/9x7Zhp2mDSi768/OwDoP+EMflaQUAjk1TQ1PoP1BOCaSvVnAh4A6g5rnLU66Qt9BHMOBYKPdIU5SzGQe8pPptHHoiyUyKS; csm-hit=tb:s-V1GX1DT0D3SGQ7KKJRGQ|1614593690782&t:1614593690864&adb:adblk_no; lc-main=zh_CN; session-id=135-5352300-7328512; session-id-time=2082787201l; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466',
    }

    async def start_requests(self):
        url = "https://www.amazon.com/-/zh/gp/site-directory?ref_=nav_em__fullstore_0_1_1_34"
        yield self.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response: Response):
        cate_data = {}
        bs = response.html_tree()
        a = bs.find_all("a", {"class": "a-link-normal fsdLink fsdDeptLink"})
        for cate in a:
            cate_data["cate_name"] = cate.get_text()
            link = "https://www.amazon.com" + cate.get("href")
            cate_data["link"] = link
            print(cate_data)
            yield self.Request(link, callback=self.parse_second_cate)

    def parse_second_cate(self, res: Response):
        bs = res.html_tree()
        data = bs.find_all("a", {"class": "a-link-normal s-navigation-item"})
        for cate in data:
            text = cate.get_text().strip()
            link = cate.get("href").strip()
            print(text, link)


CrawlCategory.start()
