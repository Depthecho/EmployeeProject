from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeModel(Base):
    """
    ORM-модель сотрудника для базы данных.
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # СВЯЗИ С ДРУГИМИ ТАБЛИЦАМИ
    # Заявки, где сотрудник является автором
    requests_created = relationship(
        "RequestModel",
        foreign_keys="[RequestModel.author_id]",
        back_populates="author"
    )

    # Заявки, где сотрудник является исполнителем
    requests_assigned = relationship(
        "RequestModel",
        foreign_keys="[RequestModel.executor_id]",
        back_populates="executor"
    )

    # ИНДЕКСЫ ДЛЯ УСКОРЕНИЯ ЗАПРОСОВ
    __table_args__ = (
        Index("idx_employees_department", "department"),  # Индекс по подразделению
        Index("idx_employees_full_name", "full_name"),  # Индекс по ФИО
    )

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, full_name='{self.full_name}')>"