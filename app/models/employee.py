from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeModel(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Связи с заявками
    requests_created = relationship(
        "RequestModel",
        foreign_keys="[RequestModel.author_id]",
        back_populates="author"
    )
    requests_assigned = relationship(
        "RequestModel",
        foreign_keys="[RequestModel.executor_id]",
        back_populates="executor"
    )

    __table_args__ = (
        Index("idx_employees_department", "department"),
        Index("idx_employees_full_name", "full_name"),
    )

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, full_name='{self.full_name}')>"