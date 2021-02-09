import json
import re
import sys
from urllib.parse import quote

import requests

if sys.platform == 'win32':
    path = 'C:\\Users\\Ety\\Desktop\\pyspider'
else:
    path = '/data/spider/pyspider'
sys.path.append(path)
import itertools

from common.spider import AsyncSpider
from service.pdd_risk import PddParamsProducer
from utils.log import get_logger

logger = get_logger('activity_find_goods')
data_queue = 'pdd_activity_find_goods'


class CrawlFindGoods(AsyncSpider):
    def get_cat_id(self, only_get_listId=False):
        """
        获取分类信息
        """
        cate_list = []
        url = 'https://mobile.yangkeduo.com/sbxeghhl.html'
        headers = {
            'authority': 'mobile.yangkeduo.com',
            'upgrade-insecure-requests': '1',
            'user-agent':
            'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
            'accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7'
        }
        ss = requests.Session()
        ss.headers = headers
        ss.stream = True
        _ = ss.get(url, timeout=10, verify=False)
        data = ss.get(url, timeout=10, verify=False).text
        ss.close()
        pattern = re.compile(r'{"store":.*}')
        result = pattern.findall(data)[0]
        result = json.loads(result)
        tab_list = result['store']['tabList']
        list_id = result['store']['listId']
        if only_get_listId:
            return list_id
        for item in tab_list:
            sub_tab = item['subTabs']
            cate_list.extend(sub_tab)
        for i in cate_list:
            i['list_id'] = list_id
        return cate_list

    @staticmethod
    def make_body(cate_info, anti_content, page):
        request_body = {
            "offset": (page - 1) * 20,
            "count": 20,
            "list_id": cate_info['list_id'] + '_' + str(cate_info['tabId']),
            "tab_id": cate_info['tabId'],
            "biz_pool_id": cate_info['bizPoolId'],
            "anti_content": anti_content
        }
        return request_body

    async def make_headers(self, nano_fp):
        ua = await self.get_ua()
        headers = {
            'Proxy-Connection':
            'keep-alive',
            'Accept':
            'application/json, text/plain, */*',
            'User-Agent':
            ua,
            'Content-Type':
            'application/json;charset=UTF-8',
            'Origin':
            'http://mobile.yangkeduo.com',
            'Referer':
            'http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_el_sn=1961510&refer_page_name=inde',
            'Accept-Language':
            'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cookie':
            f'api_uid=CkmjnGATsRdMFQBWrnXTAg==; _nano_fp={nano_fp}; ua={quote(ua)}; webp=1'
        }
        return headers

    async def start_requests(self):
        cate_list = self.get_cat_id()
        url = 'https://mobile.yangkeduo.com/proxy/api/api/lithium/query/goods_list?pdduid=0'
        api_uid = 'CkmjnGATsRdMFQBWrnXTAg=='
        referer = 'http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_name=index'
        for page, cate_info in itertools.product(range(1, 31), cate_list):
            nano_fp = await PddParamsProducer(self.session).get_nano_fp()
            headers = await self.make_headers(nano_fp)
            anti_content = await PddParamsProducer(
                self.session).get_anticontent(headers['User-Agent'], api_uid,
                                              nano_fp, referer, page)
            body = self.make_body(cate_info, anti_content, page)
            yield self.Request(
                url,
                method='POST',
                headers=headers,
                data=json.dumps(body),
                callback=self.parse,
            )

    def parse(self, response):
        print(response.json())


if __name__ == "__main__":
    CrawlFindGoods.start(env='')
