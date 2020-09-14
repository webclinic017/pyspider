import aiohttp
import json
import asyncio
from bs4 import BeautifulSoup

import sys
sys.path.append('../')

from utils import get_proxy, get_ua, get_logger, start_request

logger = get_logger('jingxi_goods_analysis')


async def make_headers(session):
    ua = await get_ua(session)
    headers = {'user-agent': ua}
    return headers


async def get_page_data(session, sku_id):
    url = f'https://m.jingxi.com/item/view?sku={sku_id}'
    headers = await make_headers(session)
    proxy = await get_proxy(session)
    res = await start_request(session,
                              url,
                              headers=headers,
                              proxy=proxy,
                              return_type='text')
    # print(res)
    bs = BeautifulSoup(res, 'lxml')
    origin_price = bs.find('div', {
        'id': 'orginBuyBtn'
    }).span.get_text().strip()[1:]
    tuan_price = bs.find('div', {'id': 'tuanBtn'}).strong.get_text().strip()[1:]
    item_name = bs.find('div', {'id': 'itemName'}).get_text().strip()
    page_data = {
        'single_price': origin_price,
        'tuan_price': tuan_price,
        'item_name': item_name
    }
    return page_data


async def get_tuancount(session, sku_id):
    url = f"https://m.jingxi.com/pingou_api/GetBatTuanNum?skuids={sku_id}&sceneval=2"
    for i in range(2):
        try:
            proxy = await get_proxy(session)
            headers = await make_headers(session)
            res = await start_request(session,
                                      url,
                                      headers=headers,
                                      proxy=proxy)
            # res = await res.text()
            # res = json.loads(res)
            sale_count = res[sku_id][0].get('tuancount', 0)
        except Exception as e:
            logger.exception(str(e))
        else:
            return sale_count


async def get_commentcount(session, sku_id):
    url = f'https://m.jingxi.com/commodity/comment/getcommentlist?version=v2&pagesize=10&score=0&sku={sku_id}&sorttype=5&page=1&t=0.17104595157127211&sceneval=2'
    comment_headers = {
        'authority': 'm.jingxi.com',
        'user-agent':
        'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Mobile Safari/537.36',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'script',
        'referer': f'https://m.jingxi.com/item/view?sku={sku_id}',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    for i in range(2):
        try:
            proxy = await get_proxy(session)
            headers = await make_headers(session)
            comment_headers.update(headers)
            res = await start_request(session,
                                      url,
                                      headers=comment_headers,
                                      proxy=proxy,
                                      return_type='text')
            res = res[10:-2]
            res = json.loads(res)
            comment_count = res['result']['productCommentSummary'][
                'CommentCount']
        except Exception as e:
            logger.exception(str(e))
        else:
            return comment_count


async def main(sku_id):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                     trust_env=True) as session:
        page_data = await get_page_data(session, sku_id)
        sale_count = await get_tuancount(session, sku_id)
        comment_count = await get_commentcount(session, sku_id)
    page_data['sale_count'] = sale_count
    page_data['comment_count'] = comment_count
    return page_data


if __name__ == "__main__":
    sku_id = '72372855972'
    data = asyncio.run(main(sku_id))
    print(data)
