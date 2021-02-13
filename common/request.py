import asyncio
import sys

import aiohttp
import async_timeout
from aiohttp import ClientSession, TCPConnector
import loguru
from .response import Response, RequestBody

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
        self.request_body = RequestBody(
            url,
            method,
            headers=headers,
            params=params,
            data=data,
            proxy=proxy,
            meta=meta,
            callback=callback,
        )
        self.timeout = timeout
        self.url = url
        self.method = method
        self.logger = logger or loguru.logger
        self.meta = meta
        self.callback = callback
        self.headers = headers
        self.params = params
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
        except Exception as e:
            self.logger.error(f"请求{self.url}出错:{repr(e)}")
        else:
            res = Response(
                self.url,
                self.method,
                text,
                resp.status,
                meta=self.meta,
                request_body=self.request_body,
                callback=self.callback,
            )
            return res
        finally:
            await self._close_request()

    async def _close_request(self):
        if self.close_request_session:
            await self.session.close()

    def copy(self):
        """Return a copy of this Request"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Request with the same attributes except for those
        given new values.
        """
        for x in [
            "url",
            "method",
            "headers",
            "params",
            "data",
            "proxy",
            "session",
            "timeout",
            "logger",
            "meta",
            "callback",
        ]:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop("cls", self.__class__)
        return cls(*args, **kwargs)

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
        timeout=20,
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
