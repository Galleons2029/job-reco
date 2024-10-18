# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 15:35
# @Author  : Galleons
# @File    : bilateral_meeting.py

"""
双选会岗位推送接口

TODO: 完善请求异常处理机制
参考： https://fastapi.tiangolo.com/tutorial/handling-errors/#reuse-fastapis-exception-handlers
"""


import os
from fastapi import FastAPI, Body, HTTPException, status, APIRouter, Depends
from fastapi.responses import Response
from typing import List

import json
import random
from bson import ObjectId
import concurrent.futures

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

from app.api.v1.endpoints.table_fill_api import client
from app.config import settings
from app.llm.prompts import prompts
from app.db.models import Job2StudentModel, Major2StudentModel, QueryRequest, JobRequestModel
from app.api.v1.dependencies import get_qdrant_client, get_xinference_client
from app.utils.embeddings import embedd_text

router = APIRouter()

from qdrant_client.http.models import Filter, FieldCondition, MatchValue, SearchRequest, HasIdCondition

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
        collection_name='bilateral_20814',
        query=embedd_text(description),  # <--- Dense vectorgp
        query_filter=Filter(
            must=[
                FieldCondition(
                    key='is_publish',
                    match=MatchValue(value=1)
                ),
                FieldCondition(
                    key='job_status',
                    match=MatchValue(value=1)
                ),
            ]
        ),
        using='job_name',
        with_payload=True,
        limit=10
    ).points

    point_ids = [result.id for result in _jobs]

    # 使用第二个命名向量对这些点重新排序
    reordered_results = client.query_points(
        collection_name='bilateral_20814',
        query=embedd_text(description),  # <--- Dense vector
        query_filter=Filter(
            must=[
                HasIdCondition(has_id=point_ids)
                # 使用 HasIdCondition 进行 ID 匹配
            ]
        ),
        using='job_name',
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