from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

from app.config import settings


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
        tokens_per_chunk=settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        model_name=settings.EMBEDDING_MODEL_ID,
    )
    chunks = []

    for section in text_split:
        chunks.extend(token_splitter.split_text(section))

    return chunks
