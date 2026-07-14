from typing import Optional, List
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import EmployeeModel
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeModel]):
    """
    Репозиторий для работы с сотрудниками.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(EmployeeModel, session)

    async def get_by_full_name(self, full_name: str) -> Optional[EmployeeModel]:
        """Поиск сотрудника по точному совпадению ФИО"""
        query = select(self.model).where(
            self.model.full_name == full_name
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_department(self, department: str) -> List[EmployeeModel]:
        """Получение всех сотрудников из указанного подразделения"""
        query = select(self.model).where(
            self.model.department == department
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_by_name(self, search: str) -> List[EmployeeModel]:
        """
        Поиск сотрудников по части ФИО (регистронезависимый).
        """
        query = select(self.model).where(
            self.model.full_name.ilike(f"%{search}%")
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_with_filters(
            self,
            department: Optional[str] = None,
            search: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[EmployeeModel]:
        """
        Расширенный метод получения сотрудников с фильтрацией и пагинацией.

        Args:
            department: Фильтр по подразделению (точное совпадение)
            search: Поиск по ФИО (поиск подстроки)
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
        """
        query = select(self.model)

        # Применение фильтра по подразделению
        if department:
            query = query.where(self.model.department == department)

        # Применение поиска по ФИО
        if search:
            query = query.where(self.model.full_name.ilike(f"%{search}%"))

        # Сортировка по ФИО для удобства
        query = query.order_by(self.model.full_name)

        # Пагинация
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_statistics(self) -> dict:
        """
        Получение статистики по сотрудникам.
        """
        # Общее количество сотрудников
        total = await self.count()

        query = select(
            self.model.department,
            func.count().label('count')
        ).group_by(self.model.department)

        result = await self.session.execute(query)
        by_department = {row[0]: row[1] for row in result.all()}

        return {
            "total": total,
            "by_department": by_department
        }