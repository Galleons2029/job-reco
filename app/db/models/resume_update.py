from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class UpdateOperation(str, Enum):
    UPDATE = "update"
    APPEND = "append"
    DELETE = "delete"

class ListUpdateOperation(BaseModel):
    operation: UpdateOperation
    field_name: str  # e.g. "work_experience", "education_experience"
    field_id_name: str  # e.g. "work_id", "education_id"
    field_id: Union[int, str]  # The ID value
    data: Optional[Dict[str, Any]] = None  # For UPDATE and APPEND operations

class ResumeUpdate(BaseModel):
    user_id: str
    basic_updates: Optional[Dict[str, Any]] = None  # 基础字段
    list_operations: Optional[List[ListUpdateOperation]] = None #嵌套列表

class BatchResumesUpdate(BaseModel):
    updates: List[ResumeUpdate] 