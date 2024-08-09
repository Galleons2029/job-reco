import json
import logging

from bson import json_util
from mq import publish_to_rabbitmq

from config import settings
from db.mongo import MongoDatabaseConnector

# 登录设置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def stream_process():
    try:
        # 建立 MongoDB 连接
        client = MongoDatabaseConnector()
        db = client["scrabble"]
        logging.info("Connected to MongoDB.")

        # 对指定集合进行监视
        changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])
        for change in changes:
            data_type = change["ns"]["coll"]
            entry_id = str(change["fullDocument"]["_id"])  # 转 ObjectId 为 string
            change["fullDocument"].pop("_id")
            change["fullDocument"]["type"] = data_type
            change["fullDocument"]["entry_id"] = entry_id

            # 用 json_util 对文档进行序列化
            data = json.dumps(change["fullDocument"], default=json_util.default)
            logging.info(f"Change detected and serialized: {data}")

            # 将数据发送至 rabbitmq
            publish_to_rabbitmq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=data)
            logging.info("数据已推送至 RabbitMQ.")

    except Exception as e:
        logging.error(f"发生了一个错误: {e}")


if __name__ == "__main__":
    stream_process()
