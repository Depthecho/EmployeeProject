from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.enums.request_status import RequestStatus


@dataclass
class Request:
    """
    Доменная модель заявки.
    """
    id: Optional[int] = None
    number: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    author_id: int = 0
    executor_id: Optional[int] = None
    description: str = ""
    deadline: datetime = field(default_factory=datetime.utcnow)
    status: RequestStatus = RequestStatus.NEW

    def __post_init__(self):
        """
        Валидация данных после инициализации.
        """
        if not self.number:
            raise ValueError("Номер заявки обязателен")
        if not self.description:
            raise ValueError("Описание заявки обязательно")
        # Проверка дедлайна только для новых заявок (без ID)
        if self.id is None and self.deadline < datetime.utcnow():
            raise ValueError("Срок выполнения не может быть в прошлом")
        if self.author_id <= 0:
            raise ValueError("ID автора должен быть положительным")

    def change_status(self, new_status: RequestStatus) -> None:
        """
        Изменение статуса заявки с проверкой допустимости перехода.
        """
        if not self.status.can_transition_to(new_status):
            raise ValueError(
                f"Невозможно перейти из статуса {self.status.value} "
                f"в статус {new_status.value}"
            )
        self.status = new_status

    def change_executor(self, new_executor_id: int) -> None:
        """
        Назначение/смена исполнителя заявки.
        """
        if new_executor_id <= 0:
            raise ValueError("ID исполнителя должен быть положительным")
        self.executor_id = new_executor_id

    @property
    def is_overdue(self) -> bool:
        """
        Проверка просроченности заявки.
        Заявка просрочена, если не завершена и дедлайн меньше текущего времени.
        """
        return (
            self.status != RequestStatus.COMPLETED
            and self.deadline < datetime.utcnow()
        )

    @property
    def days_until_deadline(self) -> int:
        """
        Количество дней до дедлайна.
        """
        delta = self.deadline - datetime.utcnow()
        return delta.days