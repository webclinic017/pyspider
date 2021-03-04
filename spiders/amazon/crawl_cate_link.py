import random
import sys

if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/pyspider"
sys.path.append(path)
from common.response import Response
from common.spider import AsyncSpider
from constants.redis_key import Amazon


class CrawlCategory(AsyncSpider):
    ua_type = "web"
    logger_name = "amazon_category"
    domain = "https://www.amazon.com"
    timeout = 5
    redis_env = "redis30"
    redis_db = 3
    concurrency = 10
    delay = random.uniform(1, 2)
    proxy = "pinzan"
    retry_time = 3

    default_headers = {
        "authority": "www.amazon.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "rtt": "200",
        # "downlink": "3.45",
        # "ect": "4g",
        "upgrade-insecure-requests": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": 'session-id=135-5352300-7328512; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466; i18n-prefs=USD; s_vnum=2046595639287%26vn%3D1; s_nr=1614595643430-New; s_dslv=1614595643432; session-id-time=2082787201l; aws_lang=cn; s_fid=3F0600BDC247E2AD-1545692182799101; s_campaign=PS%7Cacquisition_CN%7Cbaidu%7Cbz%7Cpc%7CHL%7Ctest%7Cpc%7CCN%7Cbaidu-ppc-test; s_cc=true; regStatus=pre-register; aws-target-data=%7B%22support%22%3A%221%22%7D; s_eVar60=baidu-ppc-test; aws-target-visitor-id=1614672656809-822254.38_0; aws-mkto-trk=id%3A112-TZM-766%26token%3A_mch-aws.amazon.com-1614672660855-13785; s_sq=awsamazonallprod1%3D%2526pid%253Daws.amazon.com%25252Fcn%25252Ffree%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.amazonaws.cn%25252Ffree%25252F%25253Fcs-actsft-awsft%252526sc_channel%25253Dta%252526sc_campaign%25253Dfreetier_crosslink%252526sc_countr%2526ot%253DA; session-token=T38ExGChn6hr8UP56OQiBNDvUdBxdGcijJzbuWmXnqQ4GHtrByMWfsF28wAC+HqZD6Ds9obnisToiKZag+sfpu9mVpFvmMqY94LoExqzOs88HwFQooBJ/S6nTyfPYm81m6ciPBbS4I0NBwMiJsTsBY9odv0RySfAEdrs3I3uAN5M/Zq5c0GNsvCbkI27zvFT; csm-hit=tb:s-SQ04NEDJHN0Y2QT38DY2|1614676595797&t:1614676595974&adb:adblk_no; lc-main=zh_CN; session-id=135-5352300-7328512; session-id-time=2082787201l; session-token=PwhS3q5bvjeVGnFylh3Y22M6gWaYlXjXrXnF7bmCucTg1L6//wLJz4D1/I8o97RPoWOYHJyajM53mVLG2kxHgqJglj8Is2Jd6MxLOSMJtHL343kdvHY1vQFt1/9nKPjM+dFTf59j9RklT7ZJtyDPZRvGRnO4EIqkP19Xo0GlZVNXlSIFEE6sGbfVRp99UNiJ; sp-cdn="L5Z9:CN"; ubid-main=133-5915409-7482466',
        "user-agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    }

    async def start_requests(self):
        url = "https://www.amazon.com/-/zh/gp/site-directory?ref_=nav_em__fullstore_0_1_1_34"
        yield self.Request(url, callback=self.parse)

    async def parse(self, response: Response):
        cate_data = {}
        bs = response.html_tree()
        a = bs.find_all("a", {"class": "a-link-normal fsdLink fsdDeptLink"})
        for cate in a[::-1]:
            cate_name = cate.get_text().strip()
            cate_data["cate_name"] = cate_name
            link = self.domain + cate.get("href").strip()
            self.redis_client.sadd(Amazon.CATE_LINK_SET, link)
            self.redis_client.sadd(Amazon.KEYWORD_SEARCH_SET, cate_name)
            cate_data["link"] = link
            print(cate_data)
            yield response.follow(link, callback=self.parse_second_cate)

    def parse_second_cate(self, res: Response):
        if "captchacharacters" in res.text:
            print(f"出现验证码：{res.url}")
            return res.follow(res.url)
        bs = res.html_tree()
        text = "查看所有的结果"
        if text in res.text:
            tag = bs.find(text=text).parent.parent
            url = self.domain + tag.get("href").strip()
            self.redis_client.sadd(Amazon.CATE_LINK_SET, url)
        # data = bs.find_all("a", {"class": "a-link-normal s-navigation-item"})
        try:
            data = bs.find("div", {"id": "departments"}).find_all(
                "a", {"class": "a-link-normal s-navigation-item"}
            )
        except:
            return
        if data:
            for cate in data:
                text = cate.get_text().strip()
                link = self.domain + cate.get("href").strip()
                self.redis_client.sadd(Amazon.CATE_LINK_SET, link)
                if text:
                    self.redis_client.sadd(Amazon.KEYWORD_SEARCH_SET, text)
                print(f"{text}:{link}")
                yield res.follow(link)


CrawlCategory.start()
