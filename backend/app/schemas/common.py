from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    id: Optional[UUID] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
