from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import RequestModel
from app.models.employee import EmployeeModel
from app.domain.enums.request_status import RequestStatus
from app.repositories.base import BaseRepository


class RequestRepository(BaseRepository[RequestModel]):
    """
    Репозиторий для работы с заявками.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(RequestModel, session)

    async def get_by_number(self, number: str) -> Optional[RequestModel]:
        """Поиск заявки по уникальному номеру"""
        query = select(self.model).where(self.model.number == number)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_filtered(
            self,
            status: Optional[RequestStatus] = None,
            executor_id: Optional[int] = None,
            author_id: Optional[int] = None,
            department: Optional[str] = None,
            overdue_only: bool = False,
            skip: int = 0,
            limit: int = 100
    ) -> List[RequestModel]:
        """
        Получение заявок с множественной фильтрацией.

        Args:
            status: Фильтр по статусу
            executor_id: Фильтр по исполнителю
            author_id: Фильтр по автору
            department: Фильтр по подразделению исполнителя
            overdue_only: Только просроченные заявки
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
        """
        query = select(self.model)

        # Фильтр по статусу
        if status is not None:
            query = query.where(self.model.status == status)

        # Фильтр по исполнителю
        if executor_id is not None:
            query = query.where(self.model.executor_id == executor_id)

        # Фильтр по автору
        if author_id is not None:
            query = query.where(self.model.author_id == author_id)

        # Фильтр по подразделению исполнителя (требует JOIN с EmployeeModel)
        if department is not None:
            query = query.join(EmployeeModel, self.model.executor_id == EmployeeModel.id)
            query = query.where(EmployeeModel.department == department)

        # Фильтр только просроченных заявок
        if overdue_only:
            query = query.where(
                and_(
                    self.model.deadline < datetime.utcnow(),
                    self.model.status != RequestStatus.COMPLETED
                )
            )

        # Сортировка по дедлайну (от самых срочных) и пагинация
        query = query.order_by(self.model.deadline).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_overdue_for_executor(
            self,
            executor_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[RequestModel]:
        """
        Получение просроченных заявок для конкретного исполнителя.
        Только заявки со статусом IN_PROGRESS и просроченным дедлайном.
        """
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.executor_id == executor_id,
                    self.model.status == RequestStatus.IN_PROGRESS,
                    self.model.deadline < datetime.utcnow()
                )
            )
            .order_by(self.model.deadline)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_statistics_by_status(self) -> Dict[str, int]:
        """
        Статистика заявок по статусам.

        """
        query = select(
            self.model.status,
            func.count().label('count')
        ).group_by(self.model.status)

        result = await self.session.execute(query)
        rows = result.all()

        # Преобразуем Enum в строковое значение
        return {row[0].value: row[1] for row in rows}

    async def get_statistics_by_executor(self) -> List[Dict[str, Any]]:
        """
        Топ-10 исполнителей по количеству завершенных заявок.

        """
        query = (
            select(
                EmployeeModel.id,
                EmployeeModel.full_name,
                func.count(self.model.id).label('completed_count')
            )
            .join(EmployeeModel, self.model.executor_id == EmployeeModel.id)
            .where(self.model.status == RequestStatus.COMPLETED)
            .group_by(EmployeeModel.id, EmployeeModel.full_name)
            .order_by(desc('completed_count'))
            .limit(10)
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                'employee_id': row[0],
                'full_name': row[1],
                'completed_count': row[2]
            }
            for row in rows
        ]

    async def get_next_number(self) -> str:
        """
        Генерация следующего уникального номера заявки.
        Формат: REQ-000001, REQ-000002, ...
        """
        # Извлечение максимального числового значения из номеров формата REQ-XXXXXX
        query = select(
            func.max(
                cast(
                    func.regexp_replace(self.model.number, '^REQ-', '', 'g'),
                    Integer
                )
            )
        ).where(self.model.number.startswith('REQ-'))

        result = await self.session.execute(query)
        max_num = result.scalar()

        next_num = (max_num or 0) + 1
        return f"REQ-{next_num:06d}"

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Полная статистика по заявкам.
        Агрегирует данные из нескольких методов.
        """
        # Статистика по статусам
        by_status = await self.get_statistics_by_status()

        # Количество просроченных заявок
        overdue_query = select(func.count()).where(
            and_(
                self.model.deadline < datetime.utcnow(),
                self.model.status != RequestStatus.COMPLETED
            )
        )
        result = await self.session.execute(overdue_query)
        overdue_count = result.scalar() or 0

        # Топ исполнителей
        by_executor = await self.get_statistics_by_executor()

        # Общее количество
        total = await self.count()

        return {
            "total": total,
            "by_status": by_status,
            "overdue_count": overdue_count,
            "by_executor": by_executor
        }

    async def count_filtered(
            self,
            status: Optional[RequestStatus] = None,
            executor_id: Optional[int] = None,
            author_id: Optional[int] = None,
            department: Optional[str] = None,
            overdue_only: bool = False,
            search: Optional[str] = None
    ) -> int:
        """
        Подсчет количества заявок с фильтрацией.
        Используется для пагинации в API.
        """
        query = select(func.count()).select_from(self.model)

        # Аналогичные фильтры как в get_filtered
        if status is not None:
            query = query.where(self.model.status == status)

        if executor_id is not None:
            query = query.where(self.model.executor_id == executor_id)

        if author_id is not None:
            query = query.where(self.model.author_id == author_id)

        if department is not None:
            query = query.join(EmployeeModel, self.model.executor_id == EmployeeModel.id)
            query = query.where(EmployeeModel.department == department)

        if overdue_only:
            query = query.where(
                and_(
                    self.model.deadline < datetime.utcnow(),
                    self.model.status != RequestStatus.COMPLETED
                )
            )

        # Поиск по описанию
        if search:
            query = query.where(self.model.description.ilike(f"%{search}%"))

        result = await self.session.execute(query)
        return result.scalar() or 0