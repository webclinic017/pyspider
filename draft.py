from asyncio.coroutines import iscoroutine
from typing import Any, NamedTuple, Dict


class RequestBody(NamedTuple):
    url: str
    method: str = "GET"
    headers: Dict[str, Any] = {"Content-Type": "JSON"}
    params: Any = None
    data: Any = None


a = RequestBody("a")
print(a._asdict())

import asyncio


class A:
    async def test(self):
        await asyncio.sleep(1)
        yield 1


from inspect import isawaitable, iscoroutinefunction

a = A().test
print(iscoroutinefunction(a))