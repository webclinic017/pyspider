import aiohttp
# import requests
from urllib.parse import quote
import json
import asyncio
from aiohttp import TCPConnector
import sys
sys.path.append('../')
from utils import get_logger,get_proxy,get_ua
from jingxi_spider.jingxi_category_gather import get_keyword
import re

logger=get_logger('jingxi_category_sales')

class JingXiSaleCount:
    def __init__(self):
        self.sku_id_set = set()
        self.data={'salecount':0}

      
    async def make_headers(self, session):
        headers = {
            'authority': 'm.jingxi.com',
            'user-agent':
            'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Mobile Safari/537.36',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-dest': 'script',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        ua = await get_ua(session)
        if ua:
            headers['user-agent'] = ua
        return headers


    async def get_sales(self, sku_id, session):
        url = "https://m.jingxi.com/pingou_api/GetBatTuanNum?skuids={}&sceneval=2".format(
            sku_id)
        proxy = await get_proxy(session)
        if not proxy:
            return {'msg':"can't get proxy!"}
        for i in range(2):
            try:
                headers = await self.make_headers(session)
                async with session.get(url,
                                    headers=headers,
                                    proxy=proxy,
                                    timeout=3) as res:
                    # res = requests.get(url, headers=headers, proxies=proxy).json()
                    res = await res.text()
                    # print(res)
                    res = json.loads(res)
                    # sale_count = res[sku_id][0].get('tuancount',0)
                # print(res)
            except Exception as e:
                # print(e)
                logger.exception(str(e))
            else:
                for item in list(res.values()):
                    if type(item)==list:
                        data=item[0]
                        # print(type(data))
                        sale_count=data.get('tuancount', 0)
                        if sale_count:
                            self.data['salecount'] += int(sale_count)
                break


    async def download_one(self,keyword, page, session):
        url = "https://m.jingxi.com/search/searchn?key={}&datatype=1&page={}&pagesize=10&ext_attr=no&brand_col=no&price_col=no&color_col=no&size_col=no&ext_attr_sort=no&merge_sku=yes&multi_suppliers=yes&filt_type=redisstore,1;&sort_type=sort_pingou_num_desc&frompg=1&force_merge_sku=yes&env=mobile&newpg=1&qp_disable=no&sceneval=2&traceid=996333272213842801".format(
            quote(keyword), page)
        proxy = 'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
        for i in range(2):
            try:
                headers = await self.make_headers(session)
                async with session.get(url,
                                    headers=headers,
                                    proxy=proxy,
                                    timeout=3) as resp:
                    # resp = requests.request("GET", url, headers=headers, proxies=proxy,timeout=3)
                    res = await resp.text()
                #res=res.text
                #print(res)
                response = res[9:-1]
                regex = re.compile(r'\\(?![/u"])')
                response = regex.sub(r"\\\\", response)
                response = json.loads(response)
                contents = response['data']['searchm']['Paragraph']
            except Exception as e:
                logger.exception(str(e))
                # logger.error(str(e))
            else:
                if contents:
                    for item in contents:
                        wareid = item.get('wareid')
                        if wareid:
                            # if wareid not in self.sku_id_set:
                            #     await self.get_sales(wareid, session)
                            self.sku_id_set.add(wareid)
                    break


    async def download_many(self,keyword,page):
        async with aiohttp.ClientSession(connector=TCPConnector(
                ssl=False)) as session:
            await asyncio.gather(*[
                asyncio.ensure_future(self.download_one(keyword, page_index, session))
                for page_index in range(1, page+1)
            ])
            data=list(self.sku_id_set)
            sku_list = [data[:50], data[50:]]
            for i in sku_list:
                sku_id = ','.join(i)
                # print(sku_id)
                # print(len(sku_list))
                await self.get_sales(sku_id,session)


    async def main(self,keyword,page):
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # asyncio.run(download_many(keyword), debug=True)
        # loop.run_until_complete(download_many(keyword))
        page = int(page)
        page=10
        await self.download_many(keyword,page)
        self.data['cat3'] = keyword
        keyword_list = await get_keyword()
        for item in keyword_list:
            if keyword in item.values():
                self.data['cat1']=item['cat1']
                self.data['cat2']=item['cat2']
        return self.data


if __name__ == "__main__":
    keyword = '连衣裙'
    result = asyncio.run(JingXiSaleCount().main(keyword,page=10))
    print(result)