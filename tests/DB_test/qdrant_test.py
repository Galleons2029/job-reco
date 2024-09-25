from qdrant_client import QdrantClient, models

client = QdrantClient(url="localhost:6333")

#client.create_collection(
#    collection_name="{collection_name}",
#    vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
#)
# client.create_collection(
#     collection_name="{collection_name}",
#     vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
#     init_from=models.InitFrom(collection="{from_collection_name}"),
# )
from xinference.client import Client

client2 = Client("http://192.168.100.111:9997")
model = client2.get_model("bge-small-zh-v1.5")

result = client.query_points(
    collection_name="vector_posts",
    query=model.create_embedding("产品经理如何设计原型")['data'][0]['embedding'], # <--- Dense vector
)

print(result)  # Qdrant对象:QueryResponse
print(len(result.points))  # 列表
print(result.points[0])  # Qdrant对象:ScoredPoint
print()
print(result.points[1].score)  # Qdrant对象:ScoredPoint

print(result.points[0].payload)  # 字典
print(type(result.points[0].payload))


result2 = client.search(
    collection_name="vector_posts",
    query_vector=model.create_embedding("产品经理如何设计原型")['data'][0]['embedding'], # <--- Dense vector
)

print(type(result2))
print(result2)
print(len(result2))
