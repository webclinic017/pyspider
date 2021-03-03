import json
import sys

if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/pyspider"
sys.path.append(path)
from common.response import Response
from common.spider import AsyncSpider
from constants.redis_key import Amazon


class CrawlGoodsList(AsyncSpider):
    redis_env = "test"
    redis_db = 0
    ua_type = "web"
    proxy = "pinzan"
    retry_time = 3
    domain = "https://www.amazon.com"

    default_headers = {
        "authority": "www.amazon.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "rtt": "200",
        "downlink": "7.45",
        "ect": "4g",
        "upgrade-insecure-requests": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.amazon.com/-/zh/gp/site-directory?ref_=nav_em__fullstore_0_1_1_34",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": 'session-id=135-5352300-7328512; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466; i18n-prefs=USD; s_vnum=2046595639287%26vn%3D1; s_nr=1614595643430-New; s_dslv=1614595643432; session-id-time=2082787201l; s_fid=3F0600BDC247E2AD-1545692182799101; aws-target-data=%7B%22support%22%3A%221%22%7D; aws-target-visitor-id=1614672656809-822254.38_0; aws-ubid-main=686-4312515-0006622; regStatus=pre-register; session-token=aSwsWeX8l7w7ynpdaJ+yX1cILBM2LWXpxeXVk0fxhBNvHJ+2TyfjhZRm709z8dAo4ZUUmWKNbV/IK2I4pK+7FW70aFdU9z2PlkDAQq4CjewheOiQc/46SILZVDv463z+9bpZObnyPSXysyXBU0jAEMeSQUHm0SfcgyfrOAMv9A2QOZX6k9D6PP0Mt30vrZEp; skin=noskin; csm-hit=tb:8AKVYTS88548WKE6PQZ7+s-WF24GRHRVSX75DZ7YZT2|1614738477414&t:1614738477414&adb:adblk_no; lc-main=zh_CN; session-id=135-5352300-7328512; session-id-time=2082787201l; session-token=HLvKjt8BUdpAwscqDBd93HEB0vaSS3oyVRXTIkB7XzwwzQOtGXkUwP2xmhv7D0qySl7OKvAmNmW+URG+Gl/vtoZgX6Pm74ZzECSU/0FEYTJ0dQOVSIFGh8zTKpafGXTpz30Lu8JNKNJW3O1tNWTLPFWyohrt6dHKfGA5xCEsHyG7CjjsrWJMVOxCk2sFtAcz; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466',
    }
    # start_urls = [
    #     "https://www.amazon.com/s?i=specialty-aps&bbn=16225020011&rh=n%3A7141123011%2Cn%3A7147442011%2Cn%3A7581687011&language=zh&_encoding=UTF8&ref=sd_allcat_nav_desktop_sa_intl_school_uniforms"
    # ]

    async def start_requests(self):
        for _ in range(1000):
            url = self.redis_client.spop(Amazon.CATE_LINK_SET)
            yield self.Request(url, callback=self.parse)

    def parse(self, response: Response):
        # print(response.text)
        if "captchacharacters" in response.text:
            print(f"出现验证码：{response.url}")
            return response.follow(response.url)
        bs = response.html_tree()
        goods_tags = bs.find_all("div", {"class": "a-section a-spacing-medium"})
        if not goods_tags:
            return
        for tag in goods_tags:
            item = {}
            item["asin_id"] = tag.parent.parent.parent.parent.get("data-asin")
            item["img_url"] = tag.find("img").get("src")
            item["goods_name"] = tag.find("img").get("alt")
            try:
                item["star_rating"] = tag.find("span", {"class": "a-icon-alt"}).string
            except:
                item["star_rating"] = ""
            try:
                item["price"] = tag.find("span", {"class": "a-offscreen"}).string
            except:
                item["price"] = ""
            try:
                item["goods_detail_link"] = self.domain + tag.find(
                    "a", {"class": "a-link-normal s-no-outline"}
                ).get("href")
                self.redis_client.sadd(
                    Amazon.GOODS_DEATAIL_LINK_SET, item["goods_detail_link"]
                )
            except:
                item["goods_detail_link"] = ""
            try:
                item["goods_comment_num"] = tag.find(
                    "span", {"class": "a-size-base"}
                ).string
            except:
                item["goods_comment_num"] = ""
            try:
                item["goods_comment_link"] = self.domain + tag.find(
                    "span", {"class": "a-size-base"}
                ).parent.get("href")
            except:
                item["goods_comment_link"] = ""
            print(item)
            self.redis_client.hset(
                Amazon.GOODS_LIST_ITEM_HASH,
                item["asin_id"],
                json.dumps(item, ensure_ascii=True),
            )
        try:
            next_page_url = self.domain + bs.find("li", {"class": "a-last"}).a.get(
                "href"
            )
        except:
            return
        if next_page_url:
            yield response.follow(next_page_url)


CrawlGoodsList.start()
