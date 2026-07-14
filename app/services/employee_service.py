from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy import asc, desc

from app.domain.entities.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.repositories.employee_repository import EmployeeRepository
from app.mappers.employee_mapper import EmployeeMapper
from app.models.employee import EmployeeModel


class EmployeeService:
    """Сервис для работы с сотрудниками"""

    def __init__(
            self,
            repository: EmployeeRepository,
            mapper: EmployeeMapper
    ):
        self.repository = repository
        self.mapper = mapper

    async def get_by_id(self, employee_id: int) -> Optional[EmployeeResponse]:
        """Получить сотрудника по ID"""
        orm_employee = await self.repository.get_by_id(employee_id)
        if not orm_employee:
            return None

        domain_employee = self.mapper.to_domain(orm_employee)
        return self.mapper.domain_to_response(domain_employee)

    async def get_all(
            self,
            department: Optional[str] = None,
            search: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[EmployeeResponse]:
        """Получить всех сотрудников с фильтрацией"""
        orm_employees = await self.repository.get_with_filters(
            department=department,
            search=search,
            skip=skip,
            limit=limit
        )

        domain_employees = self.mapper.to_domain_list(orm_employees)
        return [self.mapper.domain_to_response(e) for e in domain_employees]

    async def get_filtered_paginated(
            self,
            department: Optional[str] = None,
            search: Optional[str] = None,
            sort: str = "full_name_asc",
            per_page: int = 10,
            page: int = 1
    ) -> Tuple[List[EmployeeResponse], int, List[str]]:
        """
        Получить сотрудников с пагинацией и фильтрацией.
        Возвращает: (сотрудники, общее_количество, список_подразделений)
        """
        from sqlalchemy import select, func
        from app.models.employee import EmployeeModel
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            # 1. Подсчёт общего количества
            count_query = select(func.count()).select_from(EmployeeModel)

            if department:
                count_query = count_query.where(EmployeeModel.department == department)

            if search:
                count_query = count_query.where(EmployeeModel.full_name.ilike(f"%{search}%"))

            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # 2. Сортировка
            sort_mapping = {
                "full_name_asc": asc(EmployeeModel.full_name),
                "full_name_desc": desc(EmployeeModel.full_name),
                "department_asc": asc(EmployeeModel.department),
                "department_desc": desc(EmployeeModel.department),
                "created_at_desc": desc(EmployeeModel.created_at),
                "created_at_asc": asc(EmployeeModel.created_at),
            }
            order_by = sort_mapping.get(sort, asc(EmployeeModel.full_name))

            # 3. Основной запрос
            query = select(EmployeeModel)

            if department:
                query = query.where(EmployeeModel.department == department)

            if search:
                query = query.where(EmployeeModel.full_name.ilike(f"%{search}%"))

            query = query.order_by(order_by).offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            orm_employees = result.scalars().all()

            # 4. Список подразделений для фильтра
            dept_result = await session.execute(
                select(EmployeeModel.department).distinct().order_by(EmployeeModel.department)
            )
            departments = dept_result.scalars().all()

        # 5. Преобразуем в ответ
        domain_employees = self.mapper.to_domain_list(orm_employees)
        employees = [self.mapper.domain_to_response(e) for e in domain_employees]

        return employees, total, departments

    async def create(self, employee_data: EmployeeCreate) -> EmployeeResponse:
        """Создать нового сотрудника"""
        existing = await self.repository.get_by_full_name(employee_data.full_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сотрудник с ФИО '{employee_data.full_name}' уже существует"
            )

        domain_employee = self.mapper.create_to_domain(employee_data)
        orm_employee = self.mapper.to_orm(domain_employee)

        created_orm = await self.repository.create(**{
            'full_name': orm_employee.full_name,
            'department': orm_employee.department,
            'position': orm_employee.position
        })

        domain_employee.id = created_orm.id
        domain_employee.created_at = created_orm.created_at

        return self.mapper.domain_to_response(domain_employee)

    async def update(
            self,
            employee_id: int,
            employee_data: EmployeeUpdate
    ) -> Optional[EmployeeResponse]:
        """Обновить сотрудника"""
        existing = await self.repository.get_by_id(employee_id)
        if not existing:
            return None

        update_data = {}

        if employee_data.full_name is not None:
            if employee_data.full_name != existing.full_name:
                duplicate = await self.repository.get_by_full_name(employee_data.full_name)
                if duplicate and duplicate.id != employee_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Сотрудник с ФИО '{employee_data.full_name}' уже существует"
                    )
            update_data['full_name'] = employee_data.full_name

        if employee_data.department is not None:
            update_data['department'] = employee_data.department

        if employee_data.position is not None:
            update_data['position'] = employee_data.position

        updated_orm = await self.repository.update(employee_id, **update_data)
        if not updated_orm:
            return None

        domain_employee = self.mapper.to_domain(updated_orm)
        return self.mapper.domain_to_response(domain_employee)

    async def delete(self, employee_id: int) -> bool:
        """Удалить сотрудника"""
        return await self.repository.delete(employee_id)

    async def get_statistics(self) -> dict:
        """Получить статистику по сотрудникам"""
        return await self.repository.get_statistics()