import asyncio
import sys

import aiohttp
import async_timeout
import loguru
import ujson
from aiohttp import ClientSession, TCPConnector

from .response import Response

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


class Request:
    def __init__(
        self,
        url,
        method="GET",
        headers=None,
        params=None,
        data=None,
        proxy=None,
        session=None,
        timeout=5,
        logger=None,
        meta=None,
        callback=None,
    ) -> None:
        self.close_request_session = False
        if not session:
            self.session = ClientSession(connector=TCPConnector(ssl=False))
            self.close_request_session = True
        else:
            self.session = session
        self.timeout = timeout
        self.url = url
        self.method = method
        self.logger = logger or loguru.logger
        self.meta = meta
        self.callback = callback
        self.headers = headers
        self.params = params
        if isinstance(data, dict):
            self.data = ujson.dumps(data)
        else:
            self.data = data
        self.proxy = proxy

    async def fetch(self):
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.request(
                    self.method,
                    self.url,
                    headers=self.headers,
                    params=self.params,
                    data=self.data,
                    proxy=self.proxy,
                ) as resp:
                    text = await resp.text()
        except aiohttp.ClientHttpProxyError as e:
            self.logger.error(f"代理出错：{repr(e)}")
        except TimeoutError as e:
            self.logger.error(f"请求超时：{repr(e)}")
        except Exception as e:
            self.logger.error(f"{repr(e)}==>请求{self.url}出错.")
        else:
            res = Response(
                self.url,
                self.method,
                self.headers,
                text,
                resp.status,
                meta=self.meta,
                callback=self.callback,
            )
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
        method="GET",
        headers=None,
        params=None,
        data=None,
        proxy=None,
        session=None,
        timeout=5,
        logger=None,
        meta=None,
        callback=None,
    ):
        res = await cls(
            url,
            method,
            headers,
            params,
            data,
            proxy,
            session,
            timeout,
            logger=logger,
            meta=meta,
            callback=callback,
        ).fetch()
        return res


aiorequest = Request.request
