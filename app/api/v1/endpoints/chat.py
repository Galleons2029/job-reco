# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 14:46
# @Author  : Galleons
# @File    : chat.py

"""
这里是文件说明
"""
from fastapi import APIRouter, Depends, HTTPException, Body, HTTPException, status
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from app.llm.inference_pipeline import WEYON_LLM


class Query(BaseModel):
    query: str
    collections: List[str] = Field(default_factory=list)
    enable_rag: bool = Field(default=True)
    enable_evaluation: bool = False
    enable_monitoring: bool = False
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "query": "云研技术团队有什么特点？",
                "collections": [
                    "vector_posts"
                ],
                "enable_rag": True,
                "enable_evaluation": False,
                "enable_monitoring": False
            }
        },
    )


router = APIRouter()

llm = WEYON_LLM()

@router.post(
    "/query/",
    response_description="知识库查询",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def predict(messages: Query = Body(...)):
    """
    RAG知识库查询。

    根据选定的集合进行向量库检索。
    """
    answer = llm.generate(
        query=messages.query,
        collections=messages.collections,
        enable_rag=messages.enable_rag,
        enable_evaluation=messages.enable_evaluation,
        enable_monitoring=messages.enable_monitoring,
    )
    return answer
