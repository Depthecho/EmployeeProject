from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.domain.enums.request_status import RequestStatus


class RequestBase(BaseModel):
    author_id: int = Field(..., description="ID автора заявки")
    executor_id: Optional[int] = Field(None, description="ID исполнителя")
    description: str = Field(..., min_length=1, max_length=1000, description="Описание заявки")
    deadline: datetime = Field(..., description="Срок выполнения")

    model_config = ConfigDict(from_attributes=True)


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    deadline: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RequestStatusUpdate(BaseModel):
    new_status: RequestStatus = Field(..., description="Новый статус заявки")

    model_config = ConfigDict(from_attributes=True)


class RequestExecutorUpdate(BaseModel):
    executor_id: int = Field(..., description="ID нового исполнителя")

    model_config = ConfigDict(from_attributes=True)


class RequestResponse(RequestBase):
    id: int
    number: str
    created_at: datetime
    status: RequestStatus
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RequestFilterParams(BaseModel):
    status: Optional[RequestStatus] = None
    executor_id: Optional[int] = None
    author_id: Optional[int] = None
    department: Optional[str] = None
    overdue_only: bool = False

    model_config = ConfigDict(from_attributes=True)