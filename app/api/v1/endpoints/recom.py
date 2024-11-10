# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 16:25
# @Author  : Galleons
# @File    : recom.py

"""
这里是文件说明
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import datetime

from app.db.models.jobs import Career_talk, Response_CareerTalk
from motor.motor_asyncio import AsyncIOMotorClient


router = APIRouter()

import logging
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MongoDB setup
client = AsyncIOMotorClient("mongodb://root:weyon%40mongodb@192.168.15.79:27017,192.168.15.79:27018,192.168.15.79:27019/?replicaSet=app")
db = client["college"]

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
qdrant_connection = QdrantClient(url="192.168.100.111:6333")

from xinference.client import Client
xinference_connection = Client("http://192.168.100.111:9997")
embed_model = xinference_connection.get_model("bge-m3")

def get_collection(collection_name: str):
    """
    动态获取指定的集合。
    """
    return db.get_collection(collection_name)


@router.post(
    "/career_talk_recom/",
    response_description="宣讲会职业推荐",
    response_model=List[Response_CareerTalk],
    response_model_by_alias=False,
)
async def career_talk(quest: Career_talk) -> list[Response_CareerTalk]:
    """
    根据宣讲会ID推荐，每场宣讲会对应若干个宣讲岗位，

    最终每场返回包含最多3个元素的列表，匹配度由高到低，匹配度低于0.5的推荐岗位将不返回。
    """
    collection = get_collection(str(quest.school_id))
    student_key = quest.student_key

    student = await collection.find_one({"student_key": student_key})

    try:
        value = student['major']
    except KeyError:
        try:
            value = student['zy']
        except KeyError:
            value = "无专业"
            print("学生不存在")
    except TypeError:
        value = "无专业"
        print("学生不存在")

    result = []
    for item in quest.career_talk:
        career_talk_id = item.career_talk_id
        # 执行查询，应用过滤器来缩小搜索范围
        _jobs = qdrant_connection.query_points(
            collection_name='job_2024_1109',
            query=embed_model.create_embedding(value)['data'][0]['embedding'],  # <--- Dense vector
            query_filter=models.Filter(
                must=[
                    FieldCondition(
                        key="career_talk[]", match=models.MatchValue(value=career_talk_id)
                    ),
                    # FieldCondition(
                    #     key="end_time",
                    #     range=models.Range(
                    #         gte=datetime.datetime.now().timestamp(),
                    #         lt=None,
                    #         lte=None,
                    #     ),
                    # ),
                    # FieldCondition(
                    #     key='is_publish',
                    #     match=MatchValue(value=1)
                    # ),
                    # FieldCondition(
                    #     key='job_status',
                    #     range=models.Range(
                    #         gt=0,
                    #     ),
                    # ),
                ],
            ),
            limit=10  # 限制返回结果的数量
        ).points
        job_ids = [publish_id.payload['publish_id'] for publish_id in _jobs]

        logger.info(f"宣讲会{career_talk_id}返回岗位：{job_ids}")

        # 构建新的字典并添加到结果列表
        result.append(Response_CareerTalk(career_talk_id=career_talk_id, job_id=job_ids))
    return result




