from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EmployeeBase(BaseModel):
    """
    Базовый класс для всех схем сотрудников.
    """
    full_name: str = Field(..., min_length=2, max_length=255, description="ФИО сотрудника")
    department: str = Field(..., min_length=2, max_length=255, description="Подразделение")
    position: str = Field(..., min_length=2, max_length=255, description="Должность")

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(EmployeeBase):
    """Схема для создания сотрудника (все поля обязательны)"""
    pass


class EmployeeUpdate(BaseModel):
    """
    Схема для обновления сотрудника.
    """
    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="ФИО сотрудника")
    department: Optional[str] = Field(None, min_length=2, max_length=255, description="Подразделение")
    position: Optional[str] = Field(None, min_length=2, max_length=255, description="Должность")

    model_config = ConfigDict(from_attributes=True)


class EmployeeResponse(EmployeeBase):
    """
    Схема для ответа API.
    """
    id: int = Field(..., description="Идентификатор сотрудника")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")

    model_config = ConfigDict(from_attributes=True)


class EmployeeFilterParams(BaseModel):
    """
    Схема для параметров фильтрации сотрудников.
    """
    department: Optional[str] = Field(None, description="Фильтр по подразделению")
    search: Optional[str] = Field(None, description="Поиск по ФИО (поиск подстроки)")