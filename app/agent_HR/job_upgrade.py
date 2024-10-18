# -*- coding: utf-8 -*-
# @Time    : 2024/10/10 16:19
# @Author  : Galleons
# @File    : job_upgrade.py

"""
这里是文件说明
"""

import requests

url = "http://js.lh.rendd.cn/api/ai-push-job/get?type=1&timestamp=1723776777&page=1&pagesize=100"

payload={}
files={}
headers = {
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
}

response = requests.request("GET", url, headers=headers, data=payload, files=files)

print(response.text)

