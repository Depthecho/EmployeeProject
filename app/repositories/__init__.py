"""
Инициализация репозиториев.
"""
from app.repositories.base import BaseRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.request_repository import RequestRepository

__all__ = [
    "BaseRepository",
    "EmployeeRepository",
    "RequestRepository",
]