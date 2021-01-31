from aiohttp import ClientSession
import aiohttp
ANTI_HOST = 'http://172.16.0.27:3030'


class PddParamsProducer:
    def __init__(self, session=None):
        self.anti_v2_host = ANTI_HOST
        base_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        self.headers = {
            'User-Agent': base_ua,
        }
        self.timeout = 8
        self.close_session = False
        if session:
            self.session = session
        else:
            self.session = ClientSession(connector=aiohttp.TCPConnector(
                ssl=False))
            self.close_session = True

    async def get_nano_fp(self):
        url = self.anti_v2_host + "/antiV2Nano"
        res = await self.session.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )
        return res.text

    async def get_anticontent(
        self,
        ua,
        api_uid,
        nano_cookie_fp,
        referer,
        page=1,
        screen='1920,1040',
    ):
        url = self.anti_v2_host + '/antiV2RiskControl2'
        params = {
            'nano_cookie_fp': nano_cookie_fp,
            'nano_storage_fp': nano_cookie_fp,
            'api_uid': api_uid,
            'ua': ua,
            'href': referer,
            'page': page,
            'screen': screen,
        }
        res = await self.session.get(url, headers=self.headers, params=params)
        return res.text

    async def close_request_session(self):
        if self.close_session:
            await self.session.close()
