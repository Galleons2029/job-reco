from abc import ABC, abstractmethod
from pydantic import BaseModel

class DataModel(BaseModel):
    """
    所有数据模型的抽象类
    """

    entry_id: str
    type: str

class VectorDBDataModel(ABC, DataModel):
    """
    所有需要保存到向量数据库（例如Qdrant）的数据模型的抽象类
    """

    entry_id: int
    type: str

    @abstractmethod
    def to_payload(self) -> tuple:
        pass

