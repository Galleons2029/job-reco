# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 14:46
# @Author  : Galleons
# @File    : chat.py

"""
这里是文件说明
"""
from fastapi import APIRouter, Body, status
from typing import List, AsyncGenerator
from pydantic import BaseModel, ConfigDict, Field
from app.services.llm import
from fastapi.responses import StreamingResponse
import json
import asyncio
import time


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
                    "zsk_1"
                ],
                "enable_rag": True,
                "enable_evaluation": False,
                "enable_monitoring": False
            }
        },
    )



async def create_chat_chunks(content: str) -> AsyncGenerator[str, None]:
    """
    将内容切分成小块并按照 OpenAI 格式进行流式输出
    """
    # 模拟分词处理
    words = content.split()

    for i, word in enumerate(words):
        # 构造符合 OpenAI 格式的响应块
        chunk = {
            "id": i,
            "object": "chat.completion.chunk",
            "created": int(time.time()),  # 使用实际时间戳
            "model": "qwen-pro",
            "choices": [{
                "index": i,
                "delta": {
                    "content": word + " "
                },
                "finish_reason": None if i < len(words) - 1 else "stop"
            }]
        }

        # 第一个块需要包含role
        if i == 0:
            chunk["choices"][0]["delta"]["role"] = "assistant"

        # 转换为 SSE 格式
        yield f"data: {json.dumps(chunk)}\n\n"

        # 模拟输出延迟
        await asyncio.sleep(0.1)

    # 发送结束标记
    yield "data: [DONE]\n\n"



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


    return StreamingResponse(
        create_chat_chunks(answer),
        media_type="text/event-stream"
    )




