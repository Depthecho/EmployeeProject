"""
Назначение: Сервис для формирования отчетов.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.repositories.request_repository import RequestRepository
from app.repositories.employee_repository import EmployeeRepository
from app.models.employee import EmployeeModel
from app.models.request import RequestModel
from app.domain.enums.request_status import RequestStatus
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal


class ReportService:
    """Сервис для работы с отчетами"""

    def __init__(
            self,
            request_repository: RequestRepository,
            employee_repository: EmployeeRepository
    ):
        self.request_repository = request_repository
        self.employee_repository = employee_repository

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Получить полную статистику по заявкам и сотрудникам.
        """
        # Статистика по заявкам
        request_stats = await self.request_repository.get_statistics()

        # Статистика по сотрудникам
        employee_stats = await self.employee_repository.get_statistics()

        return {
            "requests": request_stats,
            "employees": employee_stats
        }

    async def get_statistics_with_filter(self, executor_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Получить статистику с фильтром по исполнителю.
        """
        async with AsyncSessionLocal() as session:
            # Базовый запрос для подсчёта
            query = select(func.count()).select_from(RequestModel)

            if executor_id:
                query = query.where(RequestModel.executor_id == executor_id)

            total_result = await session.execute(query)
            total_requests = total_result.scalar() or 0

            # Статистика по статусам
            by_status = {}
            for status in [RequestStatus.NEW, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]:
                status_query = select(func.count()).select_from(RequestModel).where(RequestModel.status == status)
                if executor_id:
                    status_query = status_query.where(RequestModel.executor_id == executor_id)
                status_result = await session.execute(status_query)
                by_status[status.value] = status_result.scalar() or 0

            # Просроченные
            overdue_query = select(func.count()).select_from(RequestModel).where(
                RequestModel.status != RequestStatus.COMPLETED,
                RequestModel.deadline < datetime.utcnow()
            )
            if executor_id:
                overdue_query = overdue_query.where(RequestModel.executor_id == executor_id)
            overdue_result = await session.execute(overdue_query)
            overdue_count = overdue_result.scalar() or 0

            # Топ исполнителей
            if executor_id:
                by_executor = []
                executor_stats = await session.execute(
                    select(
                        EmployeeModel.id,
                        EmployeeModel.full_name,
                        func.count(RequestModel.id).label('completed_count')
                    )
                    .join(RequestModel, RequestModel.executor_id == EmployeeModel.id, isouter=True)
                    .where(EmployeeModel.id == executor_id)
                    .where(RequestModel.status == RequestStatus.COMPLETED)
                    .group_by(EmployeeModel.id, EmployeeModel.full_name)
                )
                for row in executor_stats:
                    by_executor.append({
                        'employee_id': row[0],
                        'full_name': row[1],
                        'completed_count': row[2] or 0
                    })
            else:
                executor_stats = await session.execute(
                    select(
                        EmployeeModel.id,
                        EmployeeModel.full_name,
                        func.count(RequestModel.id).label('completed_count')
                    )
                    .join(RequestModel, RequestModel.executor_id == EmployeeModel.id)
                    .where(RequestModel.status == RequestStatus.COMPLETED)
                    .group_by(EmployeeModel.id, EmployeeModel.full_name)
                    .order_by(func.count(RequestModel.id).desc())
                    .limit(10)
                )
                by_executor = [
                    {
                        'employee_id': row[0],
                        'full_name': row[1],
                        'completed_count': row[2]
                    }
                    for row in executor_stats
                ]

        return {
            "total_requests": total_requests,
            "by_status": by_status,
            "overdue_count": overdue_count,
            "by_executor": by_executor
        }

    async def get_all_employees(self) -> List[Dict[str, Any]]:
        """
        Получить всех сотрудников для фильтра.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(EmployeeModel).order_by(EmployeeModel.full_name)
            )
            employees = result.scalars().all()

            return [
                {
                    'id': emp.id,
                    'full_name': emp.full_name,
                    'department': emp.department,
                    'position': emp.position
                }
                for emp in employees
            ]