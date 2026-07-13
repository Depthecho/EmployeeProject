from typing import Optional, List
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import EmployeeModel
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeModel]):

    def __init__(self, session: AsyncSession):
        super().__init__(EmployeeModel, session)

    async def get_by_full_name(self, full_name: str) -> Optional[EmployeeModel]:
        query = select(self.model).where(
            self.model.full_name == full_name
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_department(self, department: str) -> List[EmployeeModel]:
        query = select(self.model).where(
            self.model.department == department
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_by_name(self, search: str) -> List[EmployeeModel]:
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

        query = select(self.model)

        if department:
            query = query.where(self.model.department == department)

        if search:
            query = query.where(self.model.full_name.ilike(f"%{search}%"))

        query = query.order_by(self.model.full_name)

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_statistics(self) -> dict:
        total = await self.count()

        from sqlalchemy import func
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