from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer

from app.config import settings

from xinference.client import Client
import numpy as np

client = Client("http://192.168.100.111:9997")

#from fastembed import TextEmbedding
#embedding_model = TextEmbedding()


def embedd_text(text: str):
    #model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    #return model.encode(text)

    model = client.get_model("bge-small-zh-v1.5")
    embedding_list = model.create_embedding(text)['data'][0]['embedding']
    embedding_array = np.array(embedding_list)
    return embedding_array
    #embeddings_generator: np.ndarray = embedding_model.embed(text)
    #embeddings_text = list(embeddings_generator)[0]
    #return embeddings_text

# 代码嵌入模型
def embedd_repositories(text: str):
    #model = INSTRUCTOR("hkunlp/instructor-xl")
    #sentence = text
    #instruction = "Represent the structure of the repository"
    #return model.encode([instruction, sentence])
    model = client.get_model("bge-small-zh-v1.5")
    embedding_list = model.create_embedding(input)['data'][0]['embedding']
    embedding_array = np.array(embedding_list)
    return embedding_array
    #embeddings_generator: np.ndarray = embedding_model.embed(text)
    #embeddings_text = list(embeddings_generator)[0]
    #return embeddings_text