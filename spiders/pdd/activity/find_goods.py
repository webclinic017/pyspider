import json
import re
import asyncio
import time
import aiohttp
import requests
import sys
import redis
if sys.platform == 'win32':
    path = 'C:\\Users\\Ety\\Desktop\\pyflow'
else:
    path = '/data/spider/pyflow'
sys.path.append(path)
from utils.async_params_provider import PddParamsProducer
from utils.log import get_logger
from utils.get_proxy import get_proxy as get_ip
from worker.spider.jingxi_spider.common_utils import get_proxy

logger = write_log('activity_find_goods')
client = redis.Redis(host='172.16.16.15',
                     port=6379,
                     password='20A3NBVJnWZtNzxumYOz',
                     db=1)
data_queue = 'pdd_activity_find_goods'


def get_cat_id(only_get_listId=False):
    """
    获取分类信息
    """
    cate_list = []
    url = 'https://mobile.yangkeduo.com/sbxeghhl.html'
    headers = {
        'authority': 'mobile.yangkeduo.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
        'accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    }
    proxies = get_ip(platform='pinzan')
    # data = requests.get(url, headers=headers, timeout=3).text
    # print(data)
    ss = requests.Session()
    ss.headers = headers
    ss.stream = True
    _ = ss.get(url, proxies=proxies, timeout=3)
    data = ss.get(url, proxies=proxies, timeout=3).text
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


def make_headers(nano_fp):
    ua = get_random_ua(ua_type=2)
    headers = {
        'authority': 'mobile.yangkeduo.com',
        'accept': 'application/json, text/plain, */*',
        'user-agent': ua,
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://mobile.yangkeduo.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer':
        'http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_name=index',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cookie':
        f'api_uid=CiFJel9u8IKrTwBlVt+lAg==; _nano_fp={nano_fp}; webp=1'
    }
    return headers


async def start_request(page, cate_info, session, sem):
    url = 'https://mobile.yangkeduo.com/proxy/api/api/lithium/query/goods_list?pdduid=0'
    api_uid = 'CiFJel9u8IKrTwBlVt+lAg=='
    referer = 'http://mobile.yangkeduo.com/sbxeghhl.html?_pdd_fs=1&_pdd_nc=ffffff&_pdd_tc=00ffffff&_pdd_sbs=1&refer_page_name=index'
    for _ in range(10):
        proxy = await get_proxy(session, proxy_type='pinzan')
        nano_fp = await PddParamsProducer().get_nano_fp()
        headers = make_headers(nano_fp)
        anti_content = await PddParamsProducer().pdd_risk_v2_p(
            headers['user-agent'], api_uid, nano_fp, nano_fp, referer, page)
        body = make_body(cate_info, anti_content, page)
        try:
            async with sem:
                async with session.post(url,
                                        data=json.dumps(body),
                                        proxy=proxy,
                                        headers=headers,
                                        timeout=5) as resp:
                    res = await resp.json()
                    # logger.info(res)
                    result = res['result']
        except Exception as e:
            logger.error(f'请求出错，{e}')
        else:
            await asyncio.sleep(2)
            if result.get('data'):
                if not res.get('errorMsg'):
                    res['cache_time'] = int(time.time())
                    client.lpush(data_queue, json.dumps(res,
                                                        ensure_ascii=False))
                    return


async def main():
    for _ in range(10):
        try:
            cate_data = get_cat_id()
            logger.info(f'获取的分类：{cate_data}')
        except Exception as e:
            logger.error(f'获取分类信息出错:{e}')
        else:
            sem = asyncio.Semaphore(10)
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                    ssl=False)) as session:
                await asyncio.gather(*[
                    asyncio.create_task(
                        start_request(page, cate_info, session, sem))
                    for page in range(1, 30) for cate_info in cate_data
                ])

            break


if __name__ == "__main__":
    asyncio.run(main())
    time.sleep(3600)
