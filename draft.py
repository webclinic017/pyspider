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
    def test(self):
        # await asyncio.sleep(1)
        yield 1


from inspect import isawaitable, iscoroutinefunction,isgeneratorfunction,isasyncgenfunction

a = A().test
print(isgeneratorfunction(a))