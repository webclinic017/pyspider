from common.spider import AsyncSpider
import ujson


class KeywordSearch(AsyncSpider):
    retry_time = 0

    def make_headers(self, keyword):
        headers = {
            "authority": "m.jingxi.com",
            "accept": "application/json",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://m.jingxi.com/searchv3/jxpage?key={keyword}",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }
        return headers

    async def request(self, keyword, page):
        url = "https://m.jingxi.com/searchv3/jxjson"
        params = {
            "body": ujson.dumps(
                {
                    "isCorrect": "1",
                    "pvid": "898c77b3698057b0511d91831d908148_1613996835339",
                    "sort": "0",
                    "stock": "1",
                    "keyword": keyword,
                    "pagesize": "10",
                    "multi_select": "1",
                    "stid": 1,
                    "page": page,
                }
            ),
            "g_ty": "ajax",
            "sceneval": 1,
        }
        headers = self.make_headers(keyword)
        return await super().request(
            url,
            headers=headers,
            params=params,
        )
