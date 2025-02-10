# -*- coding: utf-8 -*-
# @Time    : 2024/12/25 11:58
# @Author  : Galleons
# @File    : rerank_test.py

"""
这里是文件说明
"""
import requests
from app.config import settings
import os

url = os.path.join(settings.Silicon_base_url, 'rerank')
print(url)

payload = {
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "Apple",
    "documents": ["苹果", "香蕉", "水果", "蔬菜"],
    "top_n": 4,
    "return_documents": False,
    "max_chunks_per_doc": 1024,
    "overlap_tokens": 80
}
headers = {
    "Authorization": f"Bearer {settings.Silicon_api_key1}",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)