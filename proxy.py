import aiohttp


class CommonProxy:
    """获取代理
    """
    def __init__(self):
        pass

    async def get_proxy(self, platform='2808'):
        if platform == 'zhilian':
            return 'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
        url = 'http://yflow.91cyt.com/api/proxyHandler/getProxy/?platform={}&wantType=1'.format(
            platform)
        try:
            async with aiohttp.ClientSession() as ssesion:
                async with ssesion.request('GET', url) as res:
                    result = await res.json()
        except Exception as e:
            print(str(e))
            return None
        else:
            proxy = result.get('data')
            if proxy:
                return 'http://' + proxy
            return None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.get_proxy()
