"""
Инициализация мапперов.
"""
from app.mappers.base import BaseMapper
from app.mappers.employee_mapper import EmployeeMapper
from app.mappers.request_mapper import RequestMapper

__all__ = [
    "BaseMapper",
    "EmployeeMapper",
    "RequestMapper",
]