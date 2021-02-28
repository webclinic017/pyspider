import itertools
import sys
import time
from urllib.parse import quote

if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/spider/pyspider"
sys.path.append(path)
from common.spider import AsyncSpider
from service.pdd_risk import PddParamsProducer
from spiders.pdd.activity.crawl_cate import get_cat_info


class CrawlFindGoods(AsyncSpider):
    key = "pdd_activity_find_goods"
    redis_env = "redis15"
    redis_db = 1
    logger_name = "activity_find_goods"

    @staticmethod
    def make_body(cate_info, anti_content, page):
        request_body = {
            "offset": (page - 1) * 20,
            "count": 20,
            "list_id": cate_info["list_id"] + "_" + str(cate_info["tabId"]),
            "tab_id": cate_info["tabId"],
            "biz_pool_id": cate_info["bizPoolId"],
            "anti_content": anti_content,
        }
        return request_body

    async def make_headers(self, nano_fp):
        ua = await self.get_ua()
        headers = {
            "Proxy-Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://mobile.yangkeduo.com",
            "Referer": "http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_el_sn=1961510&refer_page_name=inde",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": f"api_uid=CkmjnGATsRdMFQBWrnXTAg==; _nano_fp={nano_fp}; ua={quote(ua)}; webp=1",
        }
        return headers

    async def start_requests(self):
        cate_url = "https://mobile.yangkeduo.com/sbxeghhl.html"
        cate_list = get_cat_info(cate_url)
        url = "https://mobile.yangkeduo.com/proxy/api/api/lithium/query/goods_list?pdduid=0"
        api_uid = "CkmjnGATsRdMFQBWrnXTAg=="
        referer = "http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_name=index"
        for page, cate_info in itertools.product(range(1, 31), cate_list):
            nano_fp = await PddParamsProducer(self.session).get_nano_fp()
            headers = await self.make_headers(nano_fp)
            anti_content = await PddParamsProducer(self.session).get_anticontent(
                headers["User-Agent"], api_uid, nano_fp, referer, page
            )
            body = self.make_body(cate_info, anti_content, page)
            yield self.Request(
                url,
                method="POST",
                headers=headers,
                data=body,
                callback=self.parse,
            )

    def parse(self, response):
        res = response.json()
        try:
            data = res["result"]["data"]
        except KeyError as e:
            self.logger.error(f"{repr(e)},res:{res}")
        else:
            if data:
                if not res.get("errorMsg"):
                    res["cache_time"] = int(time.time())
                    return res


if __name__ == "__main__":
    CrawlFindGoods.start()
