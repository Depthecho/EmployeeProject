from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255, description="ФИО сотрудника")
    department: str = Field(..., min_length=2, max_length=255, description="Подразделение")
    position: str = Field(..., min_length=2, max_length=255, description="Должность")

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    department: Optional[str] = Field(None, min_length=2, max_length=255)
    position: Optional[str] = Field(None, min_length=2, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeFilterParams(BaseModel):
    department: Optional[str] = None
    search: Optional[str] = Field(None, description="Поиск по ФИО")