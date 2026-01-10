from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ResponseWrapper(BaseModel, Generic[T]):
    status: str
    message: str
    data: Optional[T]
