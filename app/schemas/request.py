from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.domain.enums.request_status import RequestStatus


class RequestBase(BaseModel):
    """
    Базовый класс для всех схем заявок.
    """
    author_id: int = Field(..., description="ID автора заявки")
    executor_id: Optional[int] = Field(None, description="ID исполнителя (может быть не назначен)")
    description: str = Field(..., min_length=1, max_length=1000, description="Описание заявки")
    deadline: datetime = Field(..., description="Срок выполнения")

    model_config = ConfigDict(from_attributes=True)


class RequestCreate(RequestBase):
    """Схема для создания заявки (все поля обязательны)"""
    pass


class RequestUpdate(BaseModel):
    """
    Схема для обновления заявки.
    """
    description: Optional[str] = Field(None, min_length=1, max_length=1000, description="Описание заявки")
    deadline: Optional[datetime] = Field(None, description="Новый срок выполнения")

    model_config = ConfigDict(from_attributes=True)


class RequestStatusUpdate(BaseModel):
    """
    Схема для обновления статуса заявки.
    """
    new_status: RequestStatus = Field(..., description="Новый статус заявки")

    model_config = ConfigDict(from_attributes=True)


class RequestExecutorUpdate(BaseModel):
    """
    Схема для назначения/смены исполнителя заявки.
    """
    executor_id: int = Field(..., description="ID нового исполнителя")

    model_config = ConfigDict(from_attributes=True)


class RequestResponse(RequestBase):
    """
    Схема для ответа API.
    """
    id: int = Field(..., description="Идентификатор заявки")
    number: str = Field(..., description="Уникальный номер заявки (формат REQ-XXXXXX)")
    created_at: datetime = Field(..., description="Дата создания")
    status: RequestStatus = Field(..., description="Текущий статус заявки")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")

    model_config = ConfigDict(from_attributes=True)


class RequestFilterParams(BaseModel):
    """
    Схема для параметров фильтрации заявок.
    """
    status: Optional[RequestStatus] = Field(None, description="Фильтр по статусу")
    executor_id: Optional[int] = Field(None, description="Фильтр по ID исполнителя")
    author_id: Optional[int] = Field(None, description="Фильтр по ID автора")
    department: Optional[str] = Field(None, description="Фильтр по подразделению исполнителя")
    overdue_only: bool = Field(False, description="Только просроченные заявки")

    model_config = ConfigDict(from_attributes=True)