import requests
import re
import sys
import json
sys.path.append('../')
from utils import get_ua


def get_tab1_id():
    proxies = {
        'http':
        'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'
    }
    url = 'https://mobile.yangkeduo.com/pincard_share_card_popup.html'
    headers = {
        'user-agent':
        'Mozilla/5.0 (Linux; Android 8.1.0; PBBT00 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36'
    }
    data = requests.get(url, headers=headers, timeout=3, proxies=proxies).text
    # print(data)
    pattern = re.compile(r'{"store":.*}')
    result = pattern.findall(data)[0]
    result = json.loads(result)
    rank_data = result['store']['rankData']
    tab1_set = set()
    for item in rank_data:
        if isinstance(item, dict):
            tab_id = item.get('tabId')
            if tab_id:
                tab1_set.add(tab_id)
    print(tab1_set)
    return tab1_set

get_tab1_id()