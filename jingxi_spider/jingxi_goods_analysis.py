import aiohttp
import json
import asyncio
import re
from bs4 import BeautifulSoup

import sys
import os
sys.path.append(os.pardir)

from utils import get_proxy, get_ua, start_request, get_logger

logger = get_logger('jingxi_goods_analysis')


async def make_headers(session):
    ua = await get_ua(session)
    headers = {'user-agent': ua}
    return headers


class GoodsAnalysis:
    def __init__(self):
        self.data = []

    async def get_page_data(self, session, sku_id):
        url = f'https://m.jingxi.com/item/view?sku={sku_id}'
        for i in range(3):
            headers = await make_headers(session)
            proxy = await get_proxy(session)
            res = await start_request(session,
                                      url,
                                      headers=headers,
                                      proxy=proxy,
                                      return_type='text')
            if res:
                break
        try:
            if not res:
                return None
            bs = BeautifulSoup(res, 'lxml')
            origin_price = bs.find('div', {
                'id': 'orginBuyBtn'
            }).span.get_text().strip()[1:]
            tuan_price = bs.find('div', {
                'id': 'tuanBtn'
            }).strong.get_text().strip()[1:]
            item_name = bs.find('div', {'id': 'itemName'}).get_text().strip()
        except Exception as e:
            logger.error(e)
        else:
            page_data = {
                'single_price': origin_price,
                'tuan_price': tuan_price,
                'item_name': item_name
            }
            return page_data

    async def get_tuancount(self, session, sku_id):
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
                logger.error(str(e))
            else:
                return sale_count

    async def get_commentcount(self, session, sku_id):
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
                response = res[10:-2]
                regex = re.compile(r'\\(?![/u"])')
                response = regex.sub(r"\\\\", response)
                res = json.loads(response)
                comment_count = res['result']['productCommentSummary'][
                    'CommentCount']
            except Exception as e:
                logger.error(str(e))
            else:
                return comment_count

    async def get_goods_info(self, session, sku_id):
        try:
            page_data = await self.get_page_data(session, sku_id)
            sale_count = await self.get_tuancount(session, sku_id)
            comment_count = await self.get_commentcount(session, sku_id)
        except:
            return {'msg': "can't get goods data!"}
        else:
            if page_data:
                if sale_count:
                    page_data['sale_count'] = sale_count
                if comment_count:
                    page_data['comment_count'] = comment_count
                self.data.append(page_data)

    async def main(self, sku_id_list):
        sku_id_list = list(sku_id_list)[:]
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                ssl=False, limit=50),
                                         trust_env=True) as session:
            await asyncio.gather(*[
                asyncio.ensure_future(self.get_goods_info(session, sku_id))
                for sku_id in set(sku_id_list)
            ])
        return self.data


if __name__ == "__main__":
    sku_id = [
        '65226843305', '70656272706', '71166765403', '70870903863',
        '68821915464', '70136671174', '69698279536'
    ]
    data = asyncio.run(GoodsAnalysis().main(sku_id))
    print(data)
