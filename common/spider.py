import asyncio
import logging
import random
import json

import aiohttp
from aiohttp import ClientSession


class BasicSpider():
    def __init__(self, retry_time=3, concurrency=20) -> None:
        self.session = ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.retry_time = retry_time
        self.sem = asyncio.Semaphore(concurrency)

    async def get_ua(self, ua_type="mobile"):
        random_ua_links = [
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomIosUa",
            "http://ycrawl.91cyt.com/api/v1/pdd/common/randomAndroidUa",
        ]
        url = random.choice(random_ua_links)
        if ua_type == 'web':
            url = "http://ycrawl.91cyt.com/api/v1/pdd/common/randomUa"
        try:
            async with self.session.get(url) as resp:
                res = await resp.json()
            ua = res['data']
            return ua
        except Exception as e:
            logging.error(f"获取ua出错：{e}")

    async def get_proxy(self, proxy_type='pinzan'):
        """获取代理

        Args:
            proxy_type (str, optional): [使用的代理平台]. Defaults to 'pinzan'.

        Returns:
            [str]: [proxy]
        """
        assert proxy_type in {
            'zhilian', '2808', 'dubsix', 'liebao', 'liebaoV1'
        }
        if proxy_type == 'zhilian':
            return 'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
        url = 'http://yproxy.91cyt.com/proxyHandler/getProxy/?platform={}&wantType=1'.format(
            proxy_type)
        try:
            async with self.session.request('GET', url) as res:
                result = await res.json()
        except Exception as e:
            logging.error(e)
        else:
            proxy = result.get('data')
            if proxy:
                return 'http://' + proxy

    async def _crawl(self,
                     url,
                     method='GET',
                     headers=None,
                     proxy=None,
                     data=None,
                     timeout=5,
                     return_type='json'):
        for _ in range(self.retry_time - 1):
            async with self.sem:
                try:
                    async with self.session.request(method,
                                                    url,
                                                    headers=headers,
                                                    proxy=proxy,
                                                    data=data,
                                                    timeout=timeout) as resp:
                        res = await resp.text()
                except Exception as e:
                    logging.error(e)
                else:
                    if return_type == 'json':
                        return json.loads(res)
                    return res

    async def crawl(self,
                    url,
                    headers=None,
                    method='GET',
                    data=None,
                    proxy_type='liebaoV1',
                    ua_type='mobile',
                    return_type='json',
                    timeout=5):
        proxy = await self.get_proxy(proxy_type=proxy_type)
        ua = await self.get_ua(ua_type=ua_type)
        if not headers:
            headers = {}
        if ua:
            headers['User-Agent'] = ua
        else:
            logging.warning(
                "can't get avalible random ua,will use the defult!")
        if proxy:
            res = await self._crawl(url,
                                    method=method,
                                    headers=headers,
                                    proxy=proxy,
                                    data=data,
                                    return_type=return_type,
                                    timeout=timeout)
            return res
        else:
            raise Exception("can't get proxy!")

    async def close(self):
        if self.session:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


async def test():
    async with BasicSpider() as spider:
        res = await spider.crawler("https://www.baidu.com",
                                   return_type='text',
                                   proxy_type='liebaoV1')
        print(res)


if __name__ == "__main__":
    asyncio.run(test())
