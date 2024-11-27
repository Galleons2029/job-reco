# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 15:20
# @Author  : Galleons
# @File    : dependencies.py

"""
这里是文件说明
"""
from app.config import settings

from qdrant_client import QdrantClient
from xinference.client import Client



def get_qdrant_client() -> QdrantClient:
    client = QdrantClient(settings.QDRANT_URL)
    return client


def qdrant_connection():
    client = get_qdrant_client()
    try:
        yield client
    finally:
        pass


def get_xinference_client():
    client = Client("http://192.168.100.111:9997")
    embed_model = client.get_model("bge-m3")
    return embed_model

