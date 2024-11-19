import pandas as pd
from tqdm import tqdm
from qdrant_client import QdrantClient, models
from typing import List, Dict, Any
import logging
from time import sleep
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qdrant_upload.log'),
        logging.StreamHandler()
    ]
)

# 初始化连接
qdrant_connection = QdrantClient(url="192.168.100.146:6333")
from xinference.client import Client

xinference_connection_1 = Client("http://192.168.100.111:9997")
xinference_connection_2 = Client("http://192.168.100.146:9997")
embed_model_1 = xinference_connection_1.get_model("bge-m3")
embed_model_2 = xinference_connection_2.get_model("bge-m3")

def get_embedding(text: str, model_num: int = 1):
    """获取embedding，支持故障转移"""
    try:
        model = embed_model_1 if model_num == 1 else embed_model_2
        return model.create_embedding(text)['data'][0]['embedding']
    except Exception as e:
        logging.warning(f"Error using model {model_num}: {str(e)}, trying alternate model")
        model = embed_model_2 if model_num == 1 else embed_model_1
        return model.create_embedding(text)['data'][0]['embedding']

def create_point(publish_id: int, doc: Dict[str, Any]) -> models.PointStruct:
    """创建单个数据点，并行处理embedding"""
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 并行执行三个embedding任务，随机分配到两个服务器
            future_name = executor.submit(get_embedding, doc['job_name'], 1)
            future_desc = executor.submit(get_embedding, doc['job_descript'], 2)
            future_req = executor.submit(get_embedding, doc['job_require'], 1)

            return models.PointStruct(
                id=publish_id,
                vector={
                    'job_name': future_name.result(),
                    'job_descript': future_desc.result(),
                    'job_require': future_req.result(),
                },
                payload=doc
            )
    except Exception as e:
        logging.error(f"Error creating point {publish_id}: {str(e)}")
        raise

def batch_upload_points(points: List[models.PointStruct], collection_name: str, batch_size: int = 100,
                        max_retries: int = 3):
    """分批上传数据点"""
    total_batches = (len(points) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(points), batch_size), total=total_batches, desc="Uploading batches"):
        batch = points[i:i + batch_size]
        retry_count = 0

        while retry_count < max_retries:
            try:
                qdrant_connection.upload_points(
                    collection_name=collection_name,
                    points=batch
                )
                logging.info(f"Successfully uploaded batch {i // batch_size + 1}/{total_batches}")
                break
            except Exception as e:
                retry_count += 1
                logging.warning(f"Error uploading batch {i // batch_size + 1}: {str(e)}")
                if retry_count < max_retries:
                    sleep_time = 2 ** retry_count  # 指数退避
                    logging.info(f"Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                else:
                    logging.error(f"Failed to upload batch {i // batch_size + 1} after {max_retries} retries")
                    raise

def main():
    try:
        # 读取数据
        job_names = pd.read_csv("/home/weyon2/DATA/test_data/c_job_publish.csv")
        job_names.dropna(subset=['job_name', 'job_descript', 'job_require'], inplace=True)
        json_job = job_names.to_dict(orient='records')
        # json_job = json_job[:100]

        # 创建所有点的列表
        points = []
        for doc in tqdm(json_job, total=len(json_job), desc="Creating points"):
            try:
                point = create_point(doc['publish_id'], doc)
                points.append(point)
            except Exception as e:
                logging.error(f"Failed to create point for document {doc['publish_id']}")
                continue

        # 分批上传
        batch_upload_points(
            points=points,
            # collection_name="job_2024_1119",
            collection_name="job_test3",
            batch_size=100,  # 可以根据需要调整批次大小
            max_retries=3
        )

        logging.info("Upload completed successfully")

    except Exception as e:
        logging.error(f"Upload failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()