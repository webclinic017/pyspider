import json
import re

import requests


def get_cat_info(url):
    """
    获取分类信息
    """
    cate_list = []
    headers = {
        "authority": "mobile.yangkeduo.com",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
    }
    ss = requests.Session()
    ss.headers = headers
    ss.stream = True
    _ = ss.get(url, timeout=10, verify=False)
    data = ss.get(url, timeout=10, verify=False).text
    ss.close()
    pattern = re.compile(r'{"store":.*}')
    result = pattern.findall(data)[0]
    result = json.loads(result)
    tab_list = result["store"]["tabList"]
    list_id = result["store"]["listId"]
    for item in tab_list:
        sub_tab = item["subTabs"]
        cate_list.extend(sub_tab)
    for i in cate_list:
        i["list_id"] = list_id
    return cate_list
