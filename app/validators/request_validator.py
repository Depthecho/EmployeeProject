"""
Назначение: Валидаторы бизнес-правил для заявок.
"""
from app.domain.enums.request_status import RequestStatus


class RequestValidator:
    """
    Валидатор для проверки бизнес-правил заявок.
    """

    @staticmethod
    def validate_status_transition(
            current_status: RequestStatus,
            new_status: RequestStatus
    ) -> bool:
        """
        Проверить, допустим ли переход из одного статуса в другой.

        Бизнес-правило:
        - Новая → В работе ✅
        - В работе → Выполнена ✅
        - Выполнена → ❌ (нельзя изменить)
        """
        return current_status.can_transition_to(new_status)

    @staticmethod
    def validate_executor_change(
            current_status: RequestStatus
    ) -> bool:
        """
        Проверить, можно ли менять исполнителя.

        Бизнес-правило:
        - Нельзя менять исполнителя у выполненной заявки
        """
        return current_status != RequestStatus.COMPLETED

    @staticmethod
    def validate_deadline(deadline) -> bool:
        """
        Проверить, что дедлайн не в прошлом.
        """
        from datetime import datetime
        return deadline >= datetime.utcnow()

    @staticmethod
    def get_allowed_transitions(status: RequestStatus) -> list:
        """
        Получить список допустимых переходов для статуса.
        """
        return RequestStatus.get_valid_transitions(status)