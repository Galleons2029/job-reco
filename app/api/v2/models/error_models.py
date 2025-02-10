from typing import List, Optional
from pydantic import BaseModel

class ValidationErrorDetail(BaseModel):
    field: str
    message: str
    value: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    detail: str
    validation_errors: List[ValidationErrorDetail] 