import json
import re
import sys
import os
import asyncio

import requests
import aiohttp
sys.path.append('../')
sys.path.append(os.path.abspath('.'))

from utils import common_request, get_logger

logger = get_logger('pdd_billboard_id')
tab2_id = set()
content_id = set()

headers = {
    'authority': 'mobile.yangkeduo.com',
    'accept': 'application/json, text/plain, */*',
    #'accesstoken': 'YJETA3VRJSUVVJQ2ITCTNMIIJXST2VQCDSDC3TLKF4EITBRIHL4A1111970',
    'user-agent':
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    #'verifyauthtoken': '7KVyLyIW1OqyDkITVJIgqw9992aff0c79dd580d',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'zh-CN,zh;q=0.9',
    #'Cookie': 'api_uid=CiT56l7XHZI1bQAuJy+bAg=='
}


def get_tab1_id():
    proxies = {
        'http':
        'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
    }
    url = 'https://mobile.yangkeduo.com/pincard_share_card_popup.html'
    headers = {
        'user-agent':
        'Mozilla/5.0 (Linux; Android 8.1.0; PBBT00 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36'
    }
    data = requests.get(url, headers=headers, timeout=3, proxies=proxies).text
    # print(data)
    pattern = re.compile(r'{"store":.*}')
    result = pattern.findall(data)[0]
    result = json.loads(result)
    rank_data = result['store']['rankData']
    tab1_set = set()
    for item in rank_data:
        if isinstance(item, dict):
            tab_id = item.get('tabId')
            if tab_id:
                tab1_set.add(tab_id)
    print(tab1_set)
    return tab1_set


async def get_tab2_id(tab_id, session):
    url = f'https://mobile.yangkeduo.com/proxy/api/api/george/tab/query_tab_list?resource_type=410&tab_id={tab_id}'
    for i in range(3):
        try:
            res = await common_request(session, url, headers=headers)
            tab_list = res['result'].get('list')
        except Exception as e:
            logger.exception(e)
        else:
            if tab_list:
                for item in tab_list:
                    tab_id = item['tab_id']
                    tab2_id.add(tab_id)
                break


async def get_tab2_id_set(session):
    tab1_set = get_tab1_id()
    await asyncio.gather(*[
        asyncio.create_task(get_tab2_id(tab_id, session))
        for tab_id in tab1_set
    ])


async def start_request(tab, session):
    page = 1
    while True:
        url = 'https://mobile.yangkeduo.com/proxy/api/api/george/content/query_content_list?pdduid=0&is_back=1&size=20&resource_type=1&tab_id={}&page={}&obj_count=2&type=1'
        url = url.format(tab, page)
        try:
            res = await common_request(session, url, headers=headers)
            items = res['result']['list']
        except Exception as e:
            logger.exception(str(e))
        else:
            if items:
                for item in items:
                    content_id.add(item['content_id'])
                    # content_map[item['content_id']] = item['meta_map']['list_name']
                    print('id length:', len(content_id))
                    # print('map length:',len(content_map))
            else:
                break
            page += 1
        if page > 100:
            break


async def main():
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False, limit=50)) as session:
        await get_tab2_id_set(session)
        print(len(tab2_id))
        await asyncio.gather(*[
            asyncio.create_task(start_request(tab, session))
            for tab in list(tab2_id)[:]
        ])
    with open('billboard_id.py', 'wt', encoding='utf-8') as fp:
        fp.write('billboard_id=' + str(content_id))


if __name__ == "__main__":
    asyncio.run(main())
