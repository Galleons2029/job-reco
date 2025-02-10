# -*- coding: utf-8 -*-
# @Time    : 2024/9/20 16:30
# @Author  : Galleons
# @File    : query_test.py

"""
专用于用户查询测试
"""

from app.services.rag.query_expansion import QueryExpansion
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    verbose=True,
    # callbacks=[callback],
    openai_api_key="sk-gxijztovbtakciuwjwwqyaoxarjfvhuargxkoawhuzsanssm",
    openai_api_base="https://api.siliconflow.cn/v1",
    model="Qwen/Qwen2.5-72B-Instruct",
    temperature=0,
)

query_expander = QueryExpansion()

query = "目前云研科技公司有多少人？"

from app.services.llm import GeneralChain
from app.services.llm import QueryExpansionTemplate

query_expansion_template = QueryExpansionTemplate()
prompt_template = query_expansion_template.create_template(3)
chain = GeneralChain().get_chain(
    llm=llm, output_key="expanded_queries", template=prompt_template
)

print(query)
response = chain.invoke({"question": query})
result = response["expanded_queries"]
print(result)
queries = result.strip().split(query_expansion_template.separator)

stripped_queries = [
            stripped_item for item in queries if (stripped_item := item.strip())
        ]
print(stripped_queries)


