# -*- coding: utf-8 -*-
# @Time    : 2024/9/19 16:54
# @Author  : Galleons
# @File    : embed_test.py

"""
这里是文件说明
"""

from sentence_transformers.SentenceTransformer import SentenceTransformer
from xinference.client import Client
import numpy as np

client = Client("http://192.168.100.111:9997")


def origin_embedd_text(text: str):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(text)


def embedd_text(text: str):

    model = client.get_model("bge-small-zh-v1.5")
    embedding_list = model.create_embedding(text)['data'][0]['embedding']
    embedding_array = np.array(embedding_list)
    return embedding_array


text = """
根据以上的设计和分析，服务端可分为管理系统模块，数据模型，API模块，其中API模块根据每个接口功能又分为用户模块，电影模块，场次模块，订单模块，评论模块，优惠券模块，会话模块，验证码模块，收藏模块，密码模块，模块划分非常清晰。
"""


print(origin_embedd_text(text))
print(origin_embedd_text(text).tolist())
print(type(origin_embedd_text(text)))
print(type(origin_embedd_text(text).tolist()))
print(type(embedd_text(text)))
print(client.get_model("bge-small-zh-v1.5").create_embedding(text)['data'][0]['embedding'])
print(type(client.get_model("bge-small-zh-v1.5").create_embedding(text)['data'][0]['embedding']))
