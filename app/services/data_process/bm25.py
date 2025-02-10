# -*- coding: utf-8 -*-
# @Time    : 2024/11/12 14:19
# @Author  : Galleons
# @File    : bm25.py

"""
这里是文件说明
"""

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from fastembed.sparse.bm25 import Bm25
from fastembed import SparseTextEmbedding

spase_embed = Bm25("Qdrant/bm25")
spase_embed.passage_embed("You should stay, study and sprint.")

documents = [
    "You should stay, study and sprint.",
    "History can only prepare us to be surprised yet again.",
]

model = SparseTextEmbedding(model_name="Qdrant/bm25")
embeddings = list(model.embed(documents))

print(embeddings)