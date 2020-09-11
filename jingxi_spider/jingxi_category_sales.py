import aiohttp
# import requests
from urllib.parse import quote
import json
import asyncio
from aiohttp import TCPConnector
import sys
sys.path.append('../')
from spider.utils import get_logger,get_proxy,get_ua
from spider.jingxi_spider.jingxi_category_gather import get_keyword
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
            #'referer': 'https://wq.jd.com/search/searchn?key=%E4%B8%9D%E8%A2%9C&area_ids=1,72,2819&filt_type=redisstore,1;&sort_type=sort_pingou_num_desc&sceneval=2&frompg=1&force_merge_sku=yes&env=jdm&newpg=1&sf=11&as=1&qp_disable=no&fdesc=%E5%8C%97%E4%BA%AC&t1=1599027112050&jxsid=15990271109725345238',
            'accept-language': 'zh-CN,zh;q=0.9',
            #'cookie': 'shshshfpa=b297da84-9482-79d1-540f-b706c2f3329c-1597804873; shshshfpb=tBKQSuSPRxUj0E1tVh%2F2BeA%3D%3D; __jdu=15978048731901886129247; unpl=V2_ZzNtbUUAQBImX0AEfBEMA2JQGlkRAxEVc10TXX4eXVEwC0VVclRCFnQUR11nG1wUZwsZXkBcRxdFCEdkeBBVAWMDE1VGZxBFLV0CFSNGF1wjU00zQwBBQHcJFF0uSgwDYgcaDhFTQEJ2XBVQL0oMDDdRFAhyZ0AVRQhHZHsdVANuAhdURFVDHXQIT118GV8NZAYUbXJQcyVFC0BUch1aNWYzE20AAx8XcAhOUX9UXAFvBRtcR15FF3UAR1RyEFsFZAsRWERnQiV2; __jdv=76161171|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_6f26bf7a69a74b95bec17dd8460ef9f9|1598873033636; areaId=19; ipLoc-djd=19-1607-3155-0; PCSYCityID=CN_440000_440300_440305; webp=1; mba_muid=15978048731901886129247; visitkey=58461455754517973; sc_width=375; wxmall_ptype=2; 3AB9D23F7A4B3C9B=3NDYHUGMNLTS2Y6BVPPMZFTFHQ2H5UMZYINL52XG7UFG6GPULHNMI2YL4UYVGEKU6OWXEYONZ2PQZZLPYUY4IWDOYU; TrackerID=3QJmKLoBFRqXqTzV0jXvceuP4wE7k1LSDbSGmQ08Ltv9qPwjWaIk7Ck2frUjFyOmFxOT8J0Ua08Bd-Wem5_1lNt0EbvD8s0sTtqvAmrZ3wFwukUU1E5b3OZSVcdHwfgfPI2UxKDHVxTdw7MNqRYBkg; cartLastOpTime=1598929270; kplTitleShow=1; cartNum=0; wxa_level=1; __jdc=76161171; wq_area=19_1607_0%7C3; retina=1; cid=9; jxsid=15990271109725345238; __jda=76161171.15978048731901886129247.1597804873.1599020762.1599027111.27; PPRD_P=UUID.15978048731901886129247-CT.138631.1.3; shshshfp=fe0aad28250e96b22aebb3320c745a1f; wqmnx1=MDEyNjM1MGg6Lm9hc2h5JURBJl8xMmZ0cnMsb3lvaV9kc3YmcGZfZT1lZHcmMTFkbCZjJTdCJjU3NXM1Nzc1NzY3N29hIHVuZC5pMkIvLjE0cGI1NlRsRylvNDEzYlNpLjlmN24yNDJZT09VIUgl; __wga=1599027115094.1599027111317.1598932266958.1598873053720.2.5; jxsid_s_t=1599027115145; jxsid_s_u=https%3A//wq.jd.com/search/searchn; __jdb=76161171.2.15978048731901886129247|27.1599027111; mba_sid=15990271112131258703377078298.2; shshshsID=caabd90d67dfe387c255b6c770471922_2_1599027115421'
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