from typing import Any, NamedTuple, Dict


class RequestBody(NamedTuple):
    url: str
    method: str = 'GET'
    headers: Dict[str, Any] = {'Content-Type': 'JSON'}
    params: Any = None
    data: Any = None


a = RequestBody('a')
print(a._asdict())
