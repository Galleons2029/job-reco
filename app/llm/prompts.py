# -*- coding: utf-8 -*-
# @Time    : 2024/9/20 15:11
# @Author  : Galleons
# @File    : prompts.py

"""
用来存放所以提示模板
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Prompts(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    # prompt: str = """You are an AI language model assistant. Your task is to generate {to_expand_to_n}
    # different versions of the given user question to retrieve relevant documents from a vector
    # database. By generating multiple perspectives on the user question, your goal is to help
    # the user overcome some of the limitations of the distance-based similarity search.
    # Provide these alternative questions seperated by '{separator}'.
    # Original question: {question}"""
    query_expansion: str = """你是一名AI语言模型助手，任务是为给定的用户问题生成{to_expand_to_n}个不同版本的相似问题，以便从向量数据库中检索相关文档。
    通过提供用户问题的多种视角，你的目标是帮助用户克服基于距离的相似性搜索中的某些限制。请用'{separator}'分隔这些相似问题。
    原始问题：{question}
    """


    # prompt: str = """You are an AI language model assistant. Your task is to extract information from a user question.
    # The required information that needs to be extracted is the user or author id.
    # Your response should consist of only the extracted id (e.g. 1345256), nothing else.
    # User question: {question}"""
    self_query: str = """你是一名AI语言模型助手，任务是从用户问题中提取信息。
    你需要提取的是用户或作者的ID。你的回复应只包含提取出的ID（例如：1345256），不应包含其他内容，如果没有ID相关信息则返回None。
    用户问题：{question}
    """


    # prompt: str = """You are an AI language model assistant. Your task is to rerank passages related to a query
    # based on their relevance.
    # The most relevant passages should be put at the beginning.
    # You should only pick at max {keep_top_k} passages.
    # The provided and reranked documents are separated by '{separator}'.
    #
    # The following are passages related to this query: {question}.
    #
    # Passages:
    # {passages}
    # """
    reranking: str = """你是一名AI语言模型助手，任务是在不更改文本内容的前提下根据相关性对与查询相关的段落进行重新排序。
    最相关的段落应放在最前面。你最多只能选择{keep_top_k}个段落。原始段落和重新排序后的段落用'{separator}'分隔。

    以下是与该查询相关的段落：{question}。

    段落： 
    {passages} 
    """


    # simple_prompt: str = """You are an AI language model assistant. Your task is to generate a cohesive and concise response to the user question.
    # Question: {question}
    # """
    simple_prompt: str = """你是一名AI语言模型助手。你的任务是生成一个连贯且简明的回复，以回答用户的问题。
    用户问题：{question}
    """


    # rag_prompt: str = """ You are a specialist in technical content writing. Your task is to create technical content based on a user query given a specific context
    # with additional information consisting of the user's previous writings and his knowledge.
    #
    # Here is a list of steps that you need to follow in order to solve this task:
    # Step 1: You need to analyze the user provided query : {question}
    # Step 2: You need to analyze the provided context and how the information in it relates to the user question: {context}
    # Step 3: Generate the content keeping in mind that it needs to be as cohesive and concise as possible related to the subject presented in the query and similar to the users writing style and knowledge presented in the context.
    # """
    rag_prompt: str = """ 你是一名技术内容写作专家。你的任务是根据用户查询，结合提供的上下文和用户的既有知识，撰写技术内容。

    为此，请按照以下步骤执行：
    1. 分析用户的查询：{question}，明确用户的需求。
    2. 分析提供的上下文，理解其中的信息如何与用户的问题相关：{context}。
    3. 撰写内容时，请确保语言连贯、简洁，并与上下文中用户的写作风格和知识相一致，精准回应用户的问题。
    """


    #     prompt: str = """
    #         You are an AI assistant and your task is to evaluate the output generated by another LLM.
    #         You need to follow these steps:
    #         Step 1: Analyze the user query: {query}
    #         Step 2: Analyze the response: {output}
    #         Step 3: Evaluate the generated response based on the following criteria and provide a score from 1 to 5 along with a brief justification for each criterion:
    #
    #         Evaluation:
    #         Relevance - [score]
    #         [1 sentence justification why relevance = score]
    #         Coherence - [score]
    #         [1 sentence justification why coherence = score]
    #         Conciseness - [score]
    #         [1 sentence justification why conciseness = score]
    # """
    llm_evaluation: str = """你是一名AI助手，任务是评估另一款语言模型生成的输出。请按照以下步骤进行操作：
        步骤1：分析用户的查询：{query}
        步骤2：分析生成的回复：{output}
        步骤3：根据以下标准对生成的回复进行评估，并为每个标准评分（1到5分），同时提供简短的理由。

        评估标准：
        1. 相关性 - [评分]
           [简短说明为什么相关性得此评分]
        2. 连贯性 - [评分]
           [简短说明为什么连贯性得此评分]
        3. 简洁性 - [评分]
           [简短说明为什么简洁性得此评分]
        """


    # prompt: str = """You are an AI assistant and your task is to evaluate the output generated by another LLM.
    # The other LLM generates writing content based on a user query and a given context.
    # The given context is compressed of custom data produces by a user that consists of posts, articles or code fragments.
    # Here is a list of steps you need to follow in order to solve this task:
    # Step 1: You need to analyze the user query : {query}
    # Step 2: You need to analyze the given context: {contex}
    # Step 3: You need to analyze the generated output: {output}
    # Step 4: Generate the evaluation
    # When doing the evaluation step you need to take the following into consideration the following:
    # -The evaluation needs to have some sort of metrics.
    # -The generated content needs to be evaluated based on the writing similarity form the context.
    # -The generated content needs to be evaluated based on its coherence and conciseness related to the given query and context.
    # -The generated content needs to be evaluated based on how well it represents the user knowledge extracted from the context."""
    rag_evaluation: str = """你是一名AI助手，任务是评估由另一款语言模型生成的输出内容。
    该语言模型根据用户的查询和提供的上下文生成写作内容。提供的上下文由用户创建的自定义数据组成，包括帖子、文章或代码片段。

    为完成此任务，请按照以下步骤操作：
    步骤1：分析用户的查询：{query}
    步骤2：分析提供的上下文：{context}
    步骤3：分析生成的输出内容：{output}
    步骤4：进行评估,生成评估结果

    在评估时，需要考虑以下几点：
    - 评估应包含一些量化的指标。
    - 根据生成内容与上下文中的写作风格相似度进行评估。
    - 根据生成内容与查询和上下文的连贯性和简洁性进行评估。
    - 根据生成内容如何反映上下文中提取的用户知识进行评估。
    """


prompts = Prompts()