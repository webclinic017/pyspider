import json
import aiohttp
import asyncio
from aiohttp import TCPConnector
import sys
sys.path.append('../')

from utils import get_logger, get_proxy, get_ua

logger=get_logger('jingxi_category_gather')


async def make_headers(session):
    headers = {
        'authority': 'wq.360buyimg.com',
        'user-agent':
        'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Mobile Safari/537.36',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'script',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

    ua = await get_ua(session)
    if ua:
        headers['user-agent'] = ua
    return headers


async def start_request(session):
    headers = await make_headers(session)
    url = 'https://wq.360buyimg.com/data/coss/keyword/project/mpjsmpv11922.jsonp?sceneval=2&g_login_type=1&g_ty=ls'
    proxy = await get_proxy(session)
    if not proxy:
        return {'msg':"can't get proxy!"} 
    for i in range(3):
        try:
            async with session.get(url, headers=headers, proxy=proxy, timeout=3) as resp:
                res=await resp.text()
            res = res[7:-2]
            data = json.loads(res)
            #print(data)
        except Exception as e:
            logger.error(e)
        else:
            keyword_list = []
            list1 = data['keywordAreas']
            for cat1 in list1:
                keyword_map = {}
                keyword_map["cat1"] = cat1['areaName']
                list2 = cat1['level1words']
                for cat2 in list2:
                    keyword_map["cat2"] = cat2['keyword']
                    list3 = cat2['level2words']
                    for cat3 in list3:
                        keyword_map["cat3"] = cat3['keyword']
                        keyword_list.append(tuple(keyword_map.items()))
            keyword_list = [dict(item) for item in keyword_list]
            if keyword_list: 
                # print(keyword_list)
                # print(len(keyword_list))
                return keyword_list

async def get_keyword():
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        result = await start_request(session)
    return result


if __name__ == "__main__":
    data = asyncio.run(get_keyword())
    print(data)
    # print(len(data))
