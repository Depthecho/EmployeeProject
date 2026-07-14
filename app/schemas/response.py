from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    """
    Схема для ответа с общей статистикой по системе.
    """
    requests: Dict[str, Any] = Field(..., description="Статистика по заявкам")
    employees: Dict[str, Any] = Field(..., description="Статистика по сотрудникам")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """
    Схема для ответа с ошибкой.
    """
    success: bool = False
    error: Dict[str, Any] = Field(..., description="Детали ошибки")

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """
    Схема для пагинированного ответа.
    """
    items: List[Any] = Field(..., description="Список элементов на текущей странице")
    total: int = Field(..., description="Общее количество элементов")
    skip: int = Field(..., description="Количество пропущенных элементов")
    limit: int = Field(..., description="Лимит элементов на странице")

    class Config:
        from_attributes = True