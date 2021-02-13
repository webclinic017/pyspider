from typing import Any, NamedTuple
import ujson


class RequestBody(NamedTuple):
    url: str
    method: str = "GET"
    headers: Any = None
    params: Any = None
    data: Any = None
    proxy: Any = None
    meta: Any = None
    callback: Any = None


class Response:
    # __slots__ = ("text", "ok", "headers", "status", "meta", "request_body")

    def __init__(self, url, method, text, status, meta, request_body) -> None:
        self.url = url
        self.method = method
        self.text = text
        self.status = status
        self.meta = meta
        self.request = request_body
        self.headers = request_body.headers
        self.callback = request_body.callback

    def json(self):
        return ujson.loads(self.text)

    def follow(
        self,
        url,
        meta=None,
        method=None,
        headers=None,
        callback=None,
    ):
        method = method or self.method
        headers = headers or self.headers
        callback = callback or self.callback
        return RequestBody(
            url, method=method, headers=headers, callback=callback, meta=meta
        )
