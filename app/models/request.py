from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.domain.enums.request_status import RequestStatus


class RequestModel(Base):
    """
    ORM-модель заявки для базы данных.
    """
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    author_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    description = Column(Text, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.NEW, nullable=False)

    # СВЯЗИ С ТАБЛИЦЕЙ СОТРУДНИКОВ
    # Автор заявки (связь с EmployeeModel)
    author = relationship(
        "EmployeeModel",
        foreign_keys=[author_id],
        back_populates="requests_created"
    )

    # Исполнитель заявки (связь с EmployeeModel)
    executor = relationship(
        "EmployeeModel",
        foreign_keys=[executor_id],
        back_populates="requests_assigned"
    )

    # ИНДЕКСЫ ДЛЯ УСКОРЕНИЯ ЗАПРОСОВ
    __table_args__ = (
        # Составной индекс для фильтрации по исполнителю + статусу + дедлайну
        Index("idx_requests_executor_status_deadline", "executor_id", "status", "deadline"),
        # Индекс для фильтрации по автору + статусу
        Index("idx_requests_author_status", "author_id", "status"),
        # Индекс для фильтрации по статусу + дедлайну (просроченные заявки)
        Index("idx_requests_status_deadline", "status", "deadline"),
        # Индекс для поиска по номеру заявки
        Index("idx_requests_number", "number"),
    )

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, number='{self.number}', status='{self.status}')>"