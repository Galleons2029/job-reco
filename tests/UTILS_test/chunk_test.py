# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 14:34
# @Author  : Galleons
# @File    : chunk_test.py

"""
app.utils.chunking单元测试
"""
import app.utils.chunking as chunking

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

def chunk_text(text: str) -> list[str]:
    """
    1. 将文本划分为段落
    2. 将字符大于500的段落划分为更小的分块
    3. 保证分块间没有重叠
    :param text: 需要切分的文本
    :return: 包含切分文本分块的列表
    """
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=500,
        chunk_overlap=0
    )
    text_split = character_splitter.split_text(text)

    # 保证分块符合嵌入模型，并构建小部分重叠
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=50,
        tokens_per_chunk=256,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    )
    chunks = []

    for section in text_split:
        chunks.extend(token_splitter.split_text(section))

    return chunks





import time

def test_chunk_text_function(text: str):
    # 示例文本，用于测试

    # 记录输入
    print("Function: chunk_text")
    print("Input: ", text[:100])
    print("Input Type: ", type(text))

    # 测量函数运行时间
    start_time = time.time()
    output = chunk_text(text)
    end_time = time.time()

    # 记录输出
    print("Output: ", output[:100])
    print("Output Type: ", type(output))
    print("Number of Chunks: ", len(output))
    print("Execution Time: {:.6f} seconds".format(end_time - start_time))


if __name__ == "__main__":
    text = """
        ### LangChain 按Token拆分文本内容

        梯子教程网
        https://www.tizi365.com › topic
        SentenceTransformers. SentenceTransformersTokenTextSplitter 是专为sentence-transformer 模型设计的文本分割器。默认行为是将文本分割成适合所需使用的 ...

        按标记切分
        LangChain中文网
        https://www.langchain.asia › modules › split_by_token
        2024年6月14日 — SentenceTransformersTokenTextSplitter 是专为句子转换模型设计的文本分割器。默认行为是将文本分成适合您希望使用的句子转换模型的标记窗口的块 ...

        使用langchain与你自己的数据对话(一)：文档加载与切割原创

        CSDN博客
        https://blog.csdn.net › article › details
        2023年7月20日 — SentenceTransformersTokenTextSplitter() : 按token来分割文本; RecursiveCharacterTextSplitter():按字符串分割文本，递归地尝试按不同的分隔符进行 ...

        langchain_text_splitters.sentence_transformers.

        aidoczh.com
        http://www.aidoczh.com › html › sentence_transformers
        langchain_text_splitters.sentence_transformers .SentenceTransformersTokenTextSplitter¶ ... 使用句子模型分词器将文本拆分为标记。 创建一个新的TextSplitter。 ... 创建 ...

        SentenceTransformersTokenText...

        GitHub
        https://github.com › langchain › issues
        ·
        翻译此页
        2023年7月5日 — From what I understand, the issue you reported is about the SentenceTransformersTokenTextSplitter not preserving the original text when ...

        langchain.text_splitter.
        GitHub Pages
        https://datastax.github.io › text_splitter › lan...
        ·
        翻译此页
        2023年12月19日 — SentenceTransformersTokenTextSplitter( ... Transform sequence of documents by splitting them. Examples using SentenceTransformersTokenTextSplitter ...

        langchain 文本拆分器| Text Splitters全集原创

        CSDN博客
        https://blog.csdn.net › article › details
        2024年3月28日 — 概括地说，文本拆分器的工作方式如下: 将文本分成语义上有意义的小块（通常是句子）。 开始将这些小块组合成一个 ...

        Retrieval in LangChain: Part 2— Text Splitters | by Sushmitha

        Medium
        https://medium.com › ...
        ·
        翻译此页
        2024年3月17日 — 6. Sentence Transformers Token Text Splitter: This type is a specialized text splitter used with sentence transformer models. from langchain.
        用户还搜索了
        LangChain transformers
        Langchain tokenizer
        Langchain chunk
        SentenceTransformer GPU
        Sentencetransformers安装
        SpacyTextSplitter
        TokenTextSplitter
        RecursiveCharacterTextSplitter
        """
    # test_chunk_text_function()

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=500,
        chunk_overlap=0
    )
    text_split = character_splitter.split_text(text)

    print(type(text_split))
    print(text_split[0])
    print(text_split[1])


    retext_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",
        chunk_size=100,
        chunk_overlap=0,
    )

    text_split = retext_splitter.split_text(text)

    print(type(text_split))
    print(len(text_split))

    for i in text_split:
        print(i)
        print("|||||||||||||||||||||||||||||||||||||||||")

    print(chunking.chunk_text(text))


