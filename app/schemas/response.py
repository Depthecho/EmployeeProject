from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class ReportResponse(BaseModel):
    requests: Dict[str, Any]
    employees: Dict[str, Any]

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True