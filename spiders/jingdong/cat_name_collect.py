import aiohttp
import json
import asyncio
import requests
import sys
sys.path.append('../')

from utils import get_proxy, get_ua
from jingdong_union.data import cat1_list, cat2_list


async def make_headers(session):
    headers = {
        'authority': 'union.jd.com',
        'accept': 'application/json, text/plain, */*',
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://union.jd.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        # 'referer': 'https://union.jd.com/proManager/index?pageNo=2',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'Cookie': 'ssid="WdSr4IVgR+KtLtq0XleO2w=="'
    }
    ua = await get_ua(session, platform='web')
    if ua:
        headers['user-agent'] = ua
    return headers


def make_params(page=1, cat1_id=None, cat2_id=None, cat3_id=None):
    params = {
        "pageNo": page,
        "pageSize": 60,
        "data": {
            "categoryId": cat1_id,
            "cat2Id": cat2_id,
            "cat3Id": cat3_id
        }
    }
    return params


async def get_category(session):
    cat_list = []
    url = 'https://union.jd.com/api/goods/search'
    proxy = await get_proxy(session)
    for item in cat2_list:
        cat2_id = item['id']
        params = make_params(cat2_id=cat2_id)
        headers = await make_headers(session)
        # proxies = {'http': proxy}
        for i in range(3):
            try:
                async with session.post(url,
                                        headers=headers,
                                        proxy=proxy,
                                        data=json.dumps(params),
                                        timeout=3) as res:
                    result = await res.json()
            except Exception as e:
                print(e)
            else:
                cat3_list = result.get('data').get('catList3')
                print(cat3_list)
                if cat3_list:
                    cat_list.extend(list(cat3_list))
                break
    with open('data.py', 'at', encoding='utf-8') as fp:
        fp.write(str(cat_list))

        print(cat_list)
        # data=json.loads(data)
    # print(data)


async def main():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
            ssl=False)) as session:
        await get_category(session)


if __name__ == "__main__":
    asyncio.run(main())
