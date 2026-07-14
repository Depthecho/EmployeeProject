from enum import Enum


class RequestStatus(str, Enum):
    """
    Enum статусов заявки.
    """
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @classmethod
    def get_valid_transitions(cls, status: 'RequestStatus') -> list['RequestStatus']:
        """
        Возвращает список допустимых статусов для перехода из текущего.
        Правила переходов:
        - NEW -> IN_PROGRESS (новую можно взять в работу)
        - IN_PROGRESS -> COMPLETED (в работе можно завершить)
        """
        transitions = {
            cls.NEW: [cls.IN_PROGRESS],
            cls.IN_PROGRESS: [cls.COMPLETED],
            cls.COMPLETED: []  # Завершенную заявку нельзя менять
        }
        return transitions.get(status, [])

    def can_transition_to(self, new_status: 'RequestStatus') -> bool:
        """
        Проверяет, можно ли перейти из текущего статуса в новый.
        """
        return new_status in self.get_valid_transitions(self)