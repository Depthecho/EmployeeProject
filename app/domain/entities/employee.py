from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Employee:
    id: Optional[int] = None
    full_name: str = ""
    department: str = ""
    position: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.full_name and len(self.full_name.strip()) < 2:
            raise ValueError("ФИО должно содержать минимум 2 символа")
        if self.department and len(self.department.strip()) < 2:
            raise ValueError("Подразделение должно содержать минимум 2 символа")
        if self.position and len(self.position.strip()) < 2:
            raise ValueError("Должность должна содержать минимум 2 символа")

    @property
    def initials(self) -> str:
        parts = self.full_name.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1][0]}."
        return self.full_name

    @property
    def full_info(self) -> str:
        return f"{self.full_name} - {self.position} ({self.department})"

    def update_info(self, full_name: str, department: str, position: str) -> None:
        self.full_name = full_name
        self.department = department
        self.position = position