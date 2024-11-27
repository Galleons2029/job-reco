# -*- coding: utf-8 -*-
# @Time    : 2024/9/27 10:00
# @Author  : Galleons
# @File    : table_fill_api.py

"""
AI智能填表助手

TODO: 完善请求异常处理机制
参考： https://fastapi.tiangolo.com/tutorial/handling-errors/#reuse-fastapis-exception-handlers
"""

import os
from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.responses import Response
from typing import List
import logging
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import json
import random
from bson import ObjectId
import concurrent.futures
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

from app.config import settings
from app.llm.prompts import prompts
from app.db.models.models import JobInModel, JobOutModel, Job2StudentModel, Major2StudentModel, QueryRequest

router = APIRouter()

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.db.qdrant import QdrantClientManager

client = QdrantClient(url="192.168.100.111:6333")

from xinference.client import Client
client2 = Client("http://192.168.100.111:9997")
embed_model = client2.get_model("bge-small-zh-v1.5")
embed_model_pro = client2.get_model("bge-m3")


mini1 = ChatOpenAI(model="qwen2-mini1",openai_api_key='empty',openai_api_base="http://192.168.100.111:8011/v1",temperature=0)
mini2 = ChatOpenAI(model="qwen2-mini2",openai_api_key='empty',openai_api_base="http://192.168.100.111:8012/v1",temperature=0)


def match_item(dic: dict):
    collections = ['job_name', 'cities_name', 'education_levels', 'attribute', 'welfare']
    queries = [dic['职位名称'], dic['工作城市'], dic['学历要求'], dic['工作性质'], dic['薪酬福利']]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        search_tasks = [
            executor.submit(qdrant_search, query, collection)
            for query, collection in zip(queries, collections)
        ]
        hits = [
            # task.result() for task in concurrent.futures.as_completed(search_tasks)
            task.result() for task in search_tasks
        ]  # 等待所有线程
    dic['需求专业'] = "#".join(
        [qdrant_search(major, 'majors_name')['专业名称'] for major in dic["需求专业"].split('#')])

    return [dic] + hits

table_chain = (ChatPromptTemplate.from_template(prompts.job_item_fill)| mini1 | JsonOutputParser() | match_item )
text_chain = (ChatPromptTemplate.from_template(prompts.job_item_write) | mini2 | JsonOutputParser())
map_chain = RunnableParallel(table=table_chain, text=text_chain)

def qdrant_search(query: str, collection: str) -> dict:
    result = client.query_points(
    collection_name=collection,
    query=embed_model.create_embedding(query)['data'][0]['embedding'],  # <--- Dense vector
    ).points[0].payload
    return result


@router.post(
    "/jobs_creat/",
    response_description="添加新的招聘岗位",
    response_model=JobOutModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_job(job: JobInModel = Body(...)):
    """
    插入一条新的岗位描述。

    入参:

        company_name: 公司名
        companyIntro: 公司介绍
        positionIntro: 岗位需求及介绍

    出参：

        job_name: 岗位名称,
        parent_category: 岗位一级目录,
        second_category: 岗位二级目录',
        province: 省份,
        cities: 市区,
        attribute: 工作属性,
        education: 学历要求,
        salary: 月薪范围，用‘-’隔开,
        tempt: 职位诱惑,
        about_major: 需求专业，用“#”号隔开,
        number: 招聘人数（正整数）,
        duty: 岗位职责,
        explain: 投递说明,
        requirements: 岗位要求,
    """
    #将创建一个唯一的 `id` 并在响应中提供。
    all_tables = map_chain.invoke({
        "company": job.company_name,
        #"position": job.position_name,
        "companyIntro": job.companyIntro,
        "positionIntro": job.positionIntro,
    })

    job_item = JobOutModel(
        job_name=all_tables['table'][1]['三级'],
        parent_category=all_tables['table'][1]['一级'],
        second_category=all_tables['table'][1]['二级'],
        province=all_tables['table'][2]['省份'],
        cities=all_tables['table'][2]['市区'],
        education=all_tables['table'][3]['学历要求'],
        attribute=all_tables['table'][4]['工作属性'],
        salary=all_tables['table'][0]['月薪范围'],
        tempt=all_tables['table'][0]['职位诱惑'],
        about_major=all_tables['table'][0]['需求专业'],
        number=int(all_tables['table'][0]['招聘人数']),

        duty=all_tables['text']['岗位职责'],
        explain=all_tables['text']['投递说明'],
        requirements=all_tables['text']['岗位要求'],
    )

    return job_item



def job_fromlist(description: str):
    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            _jobs = qdrant_client.query_points(
                collection_name='job_2024_1119',
                query=embed_model_pro.create_embedding(description)['data'][0]['embedding'],  # <--- Dense vector
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
                with_payload=True,
                limit=50,
                using='job_descript',
            ).points
            job_list = [publish_id.payload['publish_id'] for publish_id in _jobs]
            return random.sample(job_list, len(job_list))
        except Exception as e:
            logger.error(f"岗位推送时出错: {str(e)}")
            raise

jobs_chain = (ChatPromptTemplate.from_template(prompts.job_match)| mini1 | StrOutputParser() | job_fromlist )


@router.post(
    "/job_recom/",
    response_description="根据学生意愿进行推荐",
    response_model=List[int],
    response_model_by_alias=False,
)
async def list_students_byinterest(desire: Job2StudentModel = Body(...)) -> List[int]:
    """
    根据意愿推荐，最终返回包含10个元素的列表，匹配度由高到低。

    响应是未分页的，限制为 10 个结果。
    """

    jobs_list = jobs_chain.invoke({
        "desire_industry": desire.desire_industry,
        "attribute": desire.attribute,
        "second_category": desire.second_category,
        "category": desire.category,
    })

    return jobs_list


@router.post(
    "/job_recom_major/",
    response_description="根据学生专业进行推荐",
    response_model=List[int],
    response_model_by_alias=False,
)
async def list_students_bymajor(Major: Major2StudentModel) -> List[int]:
    """
    根据专业推荐，最终返回包含10个元素的列表，匹配度由高到低。

    响应是未分页的，限制为 10 个结果。
    """
    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            _jobs = qdrant_client.query_points(
                collection_name='job_2024_1119',
                query=embed_model_pro.create_embedding(Major.major)['data'][0]['embedding'],  # <--- Dense vector
                using='job_descript',
            ).points

            return [publish_id.payload['publish_id'] for publish_id in _jobs]
        except Exception as e:
            logger.error(f"批量更新岗位时出错: {str(e)}")
            raise


@router.post(
    "/job_search/",
    response_description = "根据字符串对岗位库进行语义搜索",
    response_model = List[dict],
    response_model_by_alias = False,
)

async def search_qdrant(query: QueryRequest):
    if query.is_vector:
        query.content = embed_model.create_embedding(query.content)['data'][0]['embedding']
    try:
        search_result = client.query_points(
            collection_name=query.collection_name,
            query=query.content,
            with_payload=True,
            limit=query.top_k,
        ).points
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return [{'score': item.score, **item.payload} for item in search_result]




