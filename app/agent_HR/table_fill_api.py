# -*- coding: utf-8 -*-
# @Time    : 2024/9/27 10:00
# @Author  : Galleons
# @File    : table_fill_api.py

"""
AI智能填表助手
"""

import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
import json
from bson import ObjectId
import concurrent.futures

from app.config import settings
from app.llm.prompts import prompts
from app.db.models import JobInModel, JobOutModel, UpdateStudentModel, StudentCollection

tb_fill = FastAPI(
    title="AI自动填写HR招聘岗位发布信息",
    summary="接收JSON岗位、公司等描述，返回JSON表格结构",
)

from qdrant_client import QdrantClient, models
client = QdrantClient(url="localhost:6333")


from xinference.client import Client
client2 = Client("http://192.168.100.111:9997")
embed_model = client2.get_model("bge-small-zh-v1.5")

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
local_llm = ChatOpenAI(
            model="qwen2-pro",
            openai_api_key='empty',
            openai_api_base="http://192.168.100.111:8001/v1",
            temperature=0
        )

table_chain = (ChatPromptTemplate.from_template(prompts.job_item_fill)
              | local_llm
              )
text_chain = (
    ChatPromptTemplate.from_template(prompts.job_item_write) | local_llm
)

map_chain = RunnableParallel(table=table_chain, text=text_chain)




def qdrant_search(query: str, collection: str) -> dict:
    result = client.query_points(
    collection_name=collection,
    query=embed_model.create_embedding(query)['data'][0]['embedding'],  # <--- Dense vector
    ).points[0].payload
    return result

collections = ['job_name', 'cities_name', 'education', 'majors_name','welfare', 'tempt']


@tb_fill.post(
    "/jobs/",
    response_description="添加新的招聘岗位",
    response_model=JobInModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_job(job: JobInModel = Body(...)):
    """
    插入一条新的岗位描述。

    将创建一个唯一的 `id` 并在响应中提供。
    """
    table_raw = map_chain.invoke({
        "company": job.company_name,
        "position": job.position_name,
        "companyIntro": job.companyIntro,
        "positionIntro": job.positionIntro,
    })

    table = json.loads(table_raw['table'].content)
    text = json.loads(table_raw['text'].content)

    queries = [table['职位名称'], table['工作城市'], table['学历要求'], text['岗位要求'], table['薪酬福利'], table['职位诱惑']]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        search_tasks = [
            executor.submit(qdrant_search, query, collection)
            for query, collection in zip(queries, collections)
        ]

        hits = [
            task.result().points[0].payload for task in concurrent.futures.as_completed(search_tasks)
        ]  # 等待所有线程

    job_item = JobOutModel(
        job_name = hits[0]['三级'],
        parent_category = hits[0]['一级'],
        second_category = hits[1]['一级'],
        cities = hits[0]['市区'],
        attribute = hits[0]['一级'],
        education = hits[2]['学历要求'],
        salary = hits[0]['一级'],
        about_major = hits[2]['专业名称'],
        number = hits[0]['一级'],



        duty = text['岗位职责'],
        explain = text['投递说明'],
        requirements = text['岗位要求'],

    )

    return job_item


@tb_fill.get(
    "/jobs/",
    response_description="列出所有学生",
    response_model=StudentCollection,
    response_model_by_alias=False,
)
async def list_students():
    """
    列出数据库中的所有学生数据。

    响应是未分页的，限制为 1000 个结果。
    """
    return StudentCollection(students=await student_collection.find().to_list(1000))


@tb_fill.get(
    "/jobs/{id}",
    response_description="获取单个学生",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    """
    获取特定学生的记录，通过 `id` 查找。
    """
    if (
        student := await student_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"学生 {id} 未找到")





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:mongodb_CRUD",
        host="127.0.0.1",
        port=settings.MONGO_DATABASE_API_PORT,
        reload=True
    )

