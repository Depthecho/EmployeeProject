from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import RequestModel
from app.models.employee import EmployeeModel
from app.domain.enums.request_status import RequestStatus
from app.repositories.base import BaseRepository


class RequestRepository(BaseRepository[RequestModel]):

    def __init__(self, session: AsyncSession):
        super().__init__(RequestModel, session)

    async def get_by_number(self, number: str) -> Optional[RequestModel]:
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
        query = select(self.model)

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

        query = query.order_by(self.model.deadline).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_overdue_for_executor(
        self,
        executor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestModel]:
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
        query = select(
            self.model.status,
            func.count().label('count')
        ).group_by(self.model.status)

        result = await self.session.execute(query)
        rows = result.all()

        return {row[0].value: row[1] for row in rows}

    async def get_statistics_by_executor(self) -> List[Dict[str, Any]]:
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
        by_status = await self.get_statistics_by_status()

        overdue_query = select(func.count()).where(
            and_(
                self.model.deadline < datetime.utcnow(),
                self.model.status != RequestStatus.COMPLETED
            )
        )
        result = await self.session.execute(overdue_query)
        overdue_count = result.scalar() or 0

        # По исполнителям
        by_executor = await self.get_statistics_by_executor()

        # Всего
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
        query = select(func.count()).select_from(self.model)

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

        if search:
            query = query.where(self.model.description.ilike(f"%{search}%"))

        result = await self.session.execute(query)
        return result.scalar() or 0