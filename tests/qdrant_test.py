from qdrant_client import QdrantClient, models

client = QdrantClient(url="localhost:6333")

#client.create_collection(
#    collection_name="{collection_name}",
#    vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
#)
client.create_collection(
    collection_name="{collection_name}",
    vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
    init_from=models.InitFrom(collection="{from_collection_name}"),
)
