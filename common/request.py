import asyncio
from typing import Any, NamedTuple

import aiohttp
import async_timeout
from aiohttp import ClientSession, TCPConnector
from loguru import logger
import ujson
from json import JSONDecodeError


class RequestBody(NamedTuple):
    url: str
    method: str = 'GET'
    headers: Any = None
    params: Any = None
    data: Any = None
    proxy: Any = None


class Request:
    def __init__(self,
                 url,
                 method='GET',
                 headers=None,
                 params=None,
                 data=None,
                 proxy=None,
                 session=None,
                 timeout=5,
                 return_type='json') -> None:
        self.close_request_session = False
        if not session:
            self.session = ClientSession(connector=TCPConnector(ssl=False))
            self.close_request_session = True
        self.request_body = RequestBody(
            url,
            method,
            headers=headers,
            params=params,
            data=data,
            proxy=proxy,
        )
        self.timeout = timeout
        self.return_type = return_type

    async def fetch(self):
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.request(
                        **self.request_body._asdict()) as resp:
                    res = await resp.text()
        except aiohttp.ClientHttpProxyError as e:
            logger.error(f'代理出错：{repr(e)}')
        except Exception as e:
            logger.error(f'请求出错:{repr(e)}')
        else:
            if self.return_type == 'json':
                try:
                    return ujson.loads(res)
                except JSONDecodeError as e:
                    logger.error(e)
            return res
        finally:
            await self._close_request()

    async def _close_request(self):
        if self.close_request_session:
            await self.session.close()

    @classmethod
    async def request(
        cls,
        url,
        method='GET',
        headers=None,
        params=None,
        data=None,
        proxy=None,
        session=None,
        timeout=5,
        return_type='json',
    ):
        res = await cls(url, method, headers, params, data, proxy, session,
                        timeout, return_type).fetch()
        return res


aiorequest = Request.request
res = asyncio.run(aiorequest('https://python.org', return_type='text'))
print(res)
