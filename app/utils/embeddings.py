# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 14:34
# @Author  : Galleons
# @File    : embeddings.py

"""
由于SentenceTransformer以及fastembed的调用都无法保证完全本地读取运行时接口，在调用时延时太长
所以改为调用部署在111服务器上的Xinference模型端口进行嵌入
"""
#from InstructorEmbedding import INSTRUCTOR
#from sentence_transformers.SentenceTransformer import SentenceTransformer

from app.config import settings

from xinference.client import Client
import numpy as np

client = Client("http://192.168.100.111:9997")
embed_model = client.get_model(settings.EMBEDDING_MODEL_ID)

#from fastembed import TextEmbedding
#embedding_model = TextEmbedding()


def embedd_text(text: str) -> np.ndarray:
    #model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    #return model.encode(text)

    embedding_list = embed_model.create_embedding(text)['data'][0]['embedding']
    return np.array(embedding_list)
    #embeddings_generator: np.ndarray = embedding_model.embed(text)
    #embeddings_text = list(embeddings_generator)[0]
    #return embeddings_text

# 代码嵌入模型
def embedd_repositories(text: str):
    # TODO：优化代码嵌入模型部分，寻找合适模型
    #model = INSTRUCTOR("hkunlp/instructor-xl")
    #sentence = text
    #instruction = "Represent the structure of the repository"
    #return model.encode([instruction, sentence])
    embedding_list = embed_model.create_embedding(input)['data'][0]['embedding']
    embedding_array = np.array(embedding_list)
    return embedding_array
    #embeddings_generator: np.ndarray = embedding_model.embed(text)
    #embeddings_text = list(embeddings_generator)[0]
    #return embeddings_text