# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 15:35
# @Author  : Galleons
# @File    : bilateral_meeting.py

"""
双选会岗位推送接口

TODO: 完善请求异常处理机制
参考： https://fastapi.tiangolo.com/tutorial/handling-errors/#reuse-fastapis-exception-handlers
"""

from fastapi import Body, APIRouter
from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.api.v1.endpoints.table_fill_api import client
from app.services.llm.prompts import prompts
from app.db.models.jobs import (
    JobRequestModel,
    BilateralCollection, Bilateral_delete_record, CareerTalkCollection, CareerTalkDelete
)
from app.api.v1.dependencies import get_xinference_client
from app.utils.embeddings import embedd_text

from motor.motor_asyncio import AsyncIOMotorClient

import logging
# 配置日志
logging.basicConfig(level=logging.INFO)

# MongoDB setup
mongo_connection = AsyncIOMotorClient("mongodb://root:weyon%40mongodb@192.168.15.79:27017,192.168.15.79:27018,192.168.15.79:27019/?replicaSet=app")
db = mongo_connection["college"]
job_record = mongo_connection["job_record"]

from qdrant_client import QdrantClient, models
qdrant_connection = QdrantClient(url="192.168.100.111:6333")



router = APIRouter()

embed_model = get_xinference_client()

mini1 = ChatOpenAI(model="qwen2-mini1",openai_api_key='empty',openai_api_base="http://192.168.100.111:8011/v1",temperature=0)
mini2 = ChatOpenAI(model="qwen2-mini2",openai_api_key='empty',openai_api_base="http://192.168.100.111:8012/v1",temperature=0)


def qdrant_search(query: str, collection: str) -> dict:
    result = client.query_points(
    collection_name=collection,
    query=embed_model.create_embedding(query)['data'][0]['embedding'],  # <--- Dense vector
    ).points[0].payload
    return result


def job_in_bilateral_list(description: str):
    _jobs = client.query_points(
        collection_name='job_2024_1119',
        query=embedd_text(description),  # <--- Dense vector
        # query_filter=Filter(
        #     must=[
        #         # FieldCondition(
        #         #     key="fair_list[]", match=models.MatchValue(value=career_talk_id)
        #         # ),
        #         # FieldCondition(
        #         #     key='is_publish',
        #         #     match=MatchValue(value=1)
        #         # ),
        #         # FieldCondition(
        #         #     key='job_status',
        #         #     range=models.Range(
        #         #         gt=0,
        #         #     ),
        #         # ),
        #         # FieldCondition(
        #         #     key="end_time",
        #         #     range=models.Range(
        #         #         gt=None,
        #         #         gte=datetime.datetime.now().timestamp(),
        #         #         lt=None,
        #         #         lte=None,
        #         #     ),
        #         # )
        #     ]
        # ),
        #using='job_name',
        with_payload=True,
        limit=10
    ).points

    point_ids = [result.id for result in _jobs]

    # 使用第二个命名向量对这些点重新排序
    reordered_results = client.query_points(
        collection_name='job_2024_1119',
        query=embedd_text(description),  # <--- Dense vector
        # query_filter=Filter(
        #     must=[
        #         HasIdCondition(has_id=point_ids)
        #         # 使用 HasIdCondition 进行 ID 匹配
        #     ]
        # ),
        #using='job_name',
        with_payload=True,
        limit=10
    ).points

    return [publish_id.payload['publish_id'] for publish_id in reordered_results]

bilateral_chain = (ChatPromptTemplate.from_template(prompts.job_match)| mini1 | StrOutputParser() | job_in_bilateral_list )



@router.post(
    "/bilateral_recom/",
    response_description="双选会岗位推荐",
    response_model=List[int],
    response_model_by_alias=False,
)
async def list_bilateral_recom(desire: JobRequestModel = Body(...)) -> List[int]:
    """
    根据意愿推荐，最终返回包含10个元素的列表，匹配度由高到低。

    响应是未分页的，限制为 10 个结果。
    """

    jobs_list = bilateral_chain.invoke({
        "desire_industry": desire.desire_industry,
        "attribute": desire.attribute,
        "second_category": desire.second_category,
        "category": desire.category,
    })

    return jobs_list



@router.post(
    "/bilateral_record/",
    response_description="记录新增双选会职位",
    response_model_by_alias=True,
)
async def bilateral_record(records: BilateralCollection):
    """

    """
    for record in records.data:
        publish_id = int(record.publish_id)
        ans = qdrant_connection.scroll(
            collection_name="job_2024_1109",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="publish_id", match=models.MatchValue(value=publish_id)
                    ),
                ],
            ),
            with_payload=True,
        )
        try:
            # 如果已存在career_talk列表，追加新的career_talk_id
            fair_id_list = ans[0][0].payload['fair_list']
            fair_id_list.append(int(record.fair_id))       #  append() 是在原列表上进行修改，无返回值
            # 更新payload
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"fair_list": fair_id_list},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
        except KeyError as e:
            # 如果出现异常，创建新的career_talk列表
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"fair_list": [int(record.fair_id)]},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
        except IndexError as e:
            print(f"IndexError: {e}, {record.publish_id}岗位未找到，结果为{ans}")
        except Exception as e:
            print(f"Exception: {e}")

    
    
    
    # for record in records:
    #     new_record = await job_record['bilateral'].insert_one(
    #         record.model_dump(by_alias=True, exclude=["id"])
    #     )
    #     created_record = await mongo_connection['bilateral'].find_one(
    #         {"_id": new_record.inserted_id}
    #     )

    return {"message": "双选会职位登记成功。"}


@router.post(
    "/bilateral_record_delete/",
    response_description="删除双选会职位",
    # response_model=List[int],
    response_model_by_alias=False,
)
async def bilateral_record_delete(records: Bilateral_delete_record):
    """
    从Qdrant中摸出指定双选会标签
    """

    for record in records.publish_id:
        publish_id = int(record)
        ans = qdrant_connection.scroll(
            collection_name="job_2024_1109",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="publish_id", match=models.MatchValue(value=publish_id)
                    ),
                ],
            ),
            with_payload=True,
        )
        try:
            # 提取已存在career_talk列表，删除指定career_talk_id
            fair_id_list = ans[0][0].payload['fair_list']
            fair_id_list.remove(int(records.fair_id))
            # 更新payload
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"fair_list": fair_id_list},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
        except KeyError as e:
            # 如果出现异常，创建新的career_talk列表
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"fair_list": []},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
        except ValueError:
            return {"message": "双选会ID不存在。"}

        # delete_result = await job_record['bilateral'].delete_one(
        #     {"publish_id": record, "fair_id": records.fair_id},
        # )
        #
        # if delete_result.deleted_count == 1:
        #     return Response(status_code=status.HTTP_204_NO_CONTENT)

    return {"message": "双选会职位删除成功。"}



@router.post(
    "/career_talk_record/",
    response_description="记录新增宣讲会职位",
    response_model_by_alias=True,
)
async def career_talk_record(records: CareerTalkCollection):
    """

    """
    for record in records.data:
        publish_id = int(record.publish_id)
        ans = qdrant_connection.scroll(
            collection_name="job_2024_1109",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="publish_id", match=models.MatchValue(value=publish_id)
                    ),
                ],
            ),
            with_payload=True,
        )

        try:
            # 如果已存在career_talk列表，追加新的career_talk_id
            career_jobs_list = ans[0][0].payload['career_talk']
            career_jobs_list.append(int(record.career_talk_id))  # append() 是在原列表上进行修改，无返回值
            # 更新payload
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"career_talk": career_jobs_list},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
            print(f"岗位 {record.publish_id}已有宣讲会记录，追加后宣讲会ID：{career_jobs_list}")
        except KeyError as e:
            # 如果出现异常，创建新的career_talk列表
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"career_talk": [int(record.career_talk_id)]},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
            print(f"KeyError: {e}, {record.publish_id}宣讲会列表初始化：[{record.career_talk_id}]")
        except IndexError as e:
            print(f"IndexError: {e}, {record.publish_id}岗位未找到，结果为{ans}")

        new_record = await job_record['career_talk'].insert_one(
            record.model_dump(by_alias=True)
        )
        # created_record = await mongo_connection['bilateral'].find_one(
        #     {"_id": new_record.inserted_id}
        # )

    return {"message": "宣讲会职位登记成功。"}


@router.post(
    "/career_talk_delete/",
    response_description="删除宣讲会职位",
    # response_model=List[int],
    response_model_by_alias=False,
)
async def career_talk_record_delete(records: CareerTalkDelete):
    """
    从Qdrant中找出指定宣讲会岗位并删除对应宣讲会标签
    """
    for record in records.publish_id:
        publish_id = int(record)
        ans = qdrant_connection.scroll(
            collection_name="job_2024_1109",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="publish_id", match=models.MatchValue(value=publish_id)
                    ),
                ],
            ),
            with_payload=True,
        )
        try:
            # 提取已存在career_talk列表，删除指定career_talk_id
            career_jobs_list = ans[0][0].payload['career_talk']
            career_jobs_list.remove(int(records.career_talk_id))
            # 更新payload
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"career_talk": career_jobs_list},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
        except KeyError as e:
            # 如果出现异常，创建新的career_talk列表
            qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload={"career_talk": []},
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
        except ValueError:
            return {"message": "双选会ID不存在。"}

        # delete_result = await job_record['career_talk'].delete_one(
        #     {"publish_id": record, "career_talk_id": records.career_talk_id},
        # )
        #
        # if delete_result.deleted_count == 1:
        #     return Response(status_code=status.HTTP_204_NO_CONTENT)

    return {"message": "宣讲会职位删除成功。"}
