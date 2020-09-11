import requests
import json

url = "https://union.jd.com/api/goods/search"

payload = "{\r\n    \"pageNo\": 100,\r\n    \"pageSize\": 60,\r\n    \"data\": {\r\n        \"categoryId\": null,\r\n        \"cat2Id\": null,\r\n        \"cat3Id\": null\r\n    }\r\n}"
params = json.loads(payload)
print(params)
headers = {
  'authority': 'union.jd.com',
  'accept': 'application/json, text/plain, */*',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
  'content-type': 'application/json;charset=UTF-8',
  'origin': 'https://union.jd.com',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
#   'referer': 'https://union.jd.com/proManager/index?pageNo=2',
  'accept-language': 'zh-CN,zh;q=0.9',
  'Cookie': 'pin=jd_4df5469527a52; thor=B8F069D101C3D7CDC74B0E7615F1F83450B056A940732EDAA5A3425FA69B4233256B1C3620CC13F3608FF7561AFFE3F39BE950B7B30B23964B20AE71070B1582FAA1A521BA515741D50C0AE14187D0564F16C7C9B076C6DEF5898DCA93FED3EAF8D5E96952476824CE0926166712E271BC017868C482FB5721F549E90E22B9FC1D188D4298C06A7E3EA534FA35E5FB166874717B2BCD51BAE776EB1857D42DBF'
}
# proxy={'http':'http://2020061500002101216:cXr5v1Tm1MzF4RHK@forward.apeyun.com:9082'}
response = requests.request("POST", url, headers=headers, data=payload,
# proxies=proxy
)

print(response.json())
