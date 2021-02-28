import itertools
import sys
from urllib.parse import quote

if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/spider/pyspider"
sys.path.append(path)
from common.spider import AsyncSpider
from service.pdd_risk import PddParamsProducer
from utils.tools import gen_random_str


class CrawlFindGoods(AsyncSpider):
    key = "pdd_spike_activate_goods_list"
    # redis_env = "redis15"
    # redis_db = 1
    logger_name = "activity_sec_kill"

    async def make_headers(self, nano_fp):
        ua = await self.get_ua()
        headers = {
            "Proxy-Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": ua,
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://mobile.yangkeduo.com",
            "Referer": "https://mobile.yangkeduo.com/spike.html?__rp_name=spike_v3&_pdd_fs=1&_pdd_tc=ffffff&_pdd_sbs=1&_pdd_nc=d4291d&refer_page_el_sn=99956&refer_page_name=index",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": f"api_uid=CkmjnGATsRdMFQBWrnXTAg==; _nano_fp={nano_fp}; ua={quote(ua)}; webp=1",
        }
        return headers

    async def start_requests(self):
        cate_list = [
            {"label": "精选", "value": 0},
            {"label": "男装", "value": 9042},
            {"label": "食品", "value": 6167},
            {"label": "家纺家装", "value": 6168},
            {"label": "电脑数码", "value": 6159},
            {"label": "家电汽车", "value": 14481},
            {"label": "美妆", "value": 6170},
            {"label": "鞋靴户外", "value": 10050},
            {"label": "箱包配饰", "value": 9497},
            {"label": "洗护百货", "value": 37081},
            {"label": "水果生鲜", "value": 37100},
            {"label": "母婴童装", "value": 37101},
            {"label": "女装", "value": 37102},
            {"label": "手机", "value": 37103},
            {"label": "内衣", "value": 37104},
        ]
        api_uid = "CkmjnGATsRdMFQBWrnXTAg=="
        referer = "http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_name=index"
        for page, cate_info in itertools.product(range(1, 31), cate_list):
            tab = cate_info["value"]
            nano_fp = await PddParamsProducer(self.session).get_nano_fp()
            headers = await self.make_headers(nano_fp)
            anti_content = await PddParamsProducer(self.session).get_anticontent(
                headers["User-Agent"], api_uid, nano_fp, referer, page
            )
            rand_str = gen_random_str(10)
            url = f"https://mobile.yangkeduo.com/proxy/api/api/spike/new/channel/promotion?pdduid=0&offset={(page-1)*20}&limit=20&deduplicate_list_id={rand_str}&list_id={rand_str}_{tab}&must_buy_list_gray=1&day_type=1&tab={tab}&antiContent={anti_content}"
            yield self.Request(
                url,
                headers=headers,
                callback=self.parse,
            )

    def parse(self, response):
        res = response.json()
        try:
            data = res["items"]
        except KeyError as e:
            self.logger.error(f"{repr(e)},res:{res}")
        else:
            if data:
                if not res.get("errorMsg"):
                    # res["cache_time"] = int(time.time())
                    print(res)


if __name__ == "__main__":
    CrawlFindGoods.start()
