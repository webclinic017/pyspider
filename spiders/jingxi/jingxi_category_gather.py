import json
import sys

if sys.platform == "win32":
    path = "C:\\Users\\Ety\\Desktop\\pyspider"
else:
    path = "/data/spider/pyspider"
sys.path.append(path)

from common.response import Response
from common.spider import AsyncSpider


class CrawlCate(AsyncSpider):
    logger = "jingxi_category_gather"

    def make_headers(self):
        headers = {
            "authority": "wq.360buyimg.com",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-dest": "script",
            "accept-language": "zh-CN,zh;q=0.9",
        }
        return headers

    async def start_requests(self):
        headers = self.make_headers()
        url = "https://wq.360buyimg.com/data/coss/keyword/project/mpjsmpv11922.jsonp?sceneval=2&g_login_type=1&g_ty=ls"
        yield self.Request(url, headers=headers, callback=self.parse)

    def parse(self, response: Response):
        data = response.text
        r = data[7:-2]
        d = json.loads(r)
        keyword_list = []
        list1 = d["keywordAreas"]
        for cat1 in list1:
            keyword_map = {"cat1": cat1["areaName"]}
            list2 = cat1["level1words"]
            for cat2 in list2:
                keyword_map["cat2"] = cat2["keyword"]
                list3 = cat2["level2words"]
                for cat3 in list3:
                    keyword_map["cat3"] = cat3["keyword"]
                    keyword_list.append(tuple(keyword_map.items()))
                    print(keyword_map)
        keyword_list = [dict(item) for item in keyword_list]
        if keyword_list:
            # print(keyword_list)
            # print(len(keyword_list))
            return keyword_list


if __name__ == "__main__":
    CrawlCate.start()
