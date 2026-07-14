from typing import Optional, List, Tuple
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc

from app.domain.entities.request import Request
from app.domain.enums.request_status import RequestStatus
from app.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestResponse,
    RequestFilterParams
)
from app.repositories.request_repository import RequestRepository
from app.repositories.employee_repository import EmployeeRepository
from app.mappers.request_mapper import RequestMapper
from app.services.employee_service import EmployeeService


class RequestService:
    """Сервис для работы с заявками"""
    def __init__(
        self,
        repository: RequestRepository,
        mapper: RequestMapper,
        employee_service: EmployeeService,
        employee_repository: EmployeeRepository
    ):
        self.repository = repository
        self.mapper = mapper
        self.employee_service = employee_service
        self.employee_repository = employee_repository

    async def get_by_id(self, request_id: int) -> Optional[RequestResponse]:
        """Получить заявку по ID"""
        orm_request = await self.repository.get_by_id(request_id)
        if not orm_request:
            return None

        domain_request = self.mapper.to_domain(orm_request)
        return self.mapper.domain_to_response(domain_request)

    async def get_filtered(
            self,
            filters: RequestFilterParams,
            skip: int = 0,
            limit: int = 100
    ) -> List[RequestResponse]:
        """Получить заявки с фильтрацией"""
        orm_requests = await self.repository.get_filtered(
            status=filters.status,
            executor_id=filters.executor_id,
            author_id=filters.author_id,
            department=filters.department,
            overdue_only=filters.overdue_only,
            skip=skip,
            limit=limit
        )

        domain_requests = self.mapper.to_domain_list(orm_requests)
        return [self.mapper.domain_to_response(r) for r in domain_requests]

    async def get_filtered_paginated(
            self,
            status: Optional[str] = None,
            search: Optional[str] = None,
            sort: str = "created_at_desc",
            per_page: int = 10,
            page: int = 1
    ) -> Tuple[List[RequestResponse], int]:
        """
        Получить заявки с пагинацией и фильтрацией.
        Возвращает: (заявки, общее_количество)
        """
        from sqlalchemy import select, func
        from app.models.request import RequestModel
        from app.core.database import AsyncSessionLocal
        from app.domain.enums.request_status import RequestStatus

        # Преобразуем статус
        status_enum = None
        if status:
            try:
                status_enum = RequestStatus(status)
            except ValueError:
                pass

        async with AsyncSessionLocal() as session:
            # 1. Подсчёт общего количества
            count_query = select(func.count()).select_from(RequestModel)

            if status_enum is not None:
                count_query = count_query.where(RequestModel.status == status_enum)

            if search:
                count_query = count_query.where(RequestModel.description.ilike(f"%{search}%"))

            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # 2. Сортировка
            sort_mapping = {
                "created_at_desc": desc(RequestModel.created_at),
                "created_at_asc": asc(RequestModel.created_at),
                "deadline_asc": asc(RequestModel.deadline),
                "deadline_desc": desc(RequestModel.deadline),
                "number_asc": asc(RequestModel.number),
                "number_desc": desc(RequestModel.number),
            }
            order_by = sort_mapping.get(sort, desc(RequestModel.created_at))

            # 3. Основной запрос
            query = select(RequestModel)

            if status_enum is not None:
                query = query.where(RequestModel.status == status_enum)

            if search:
                query = query.where(RequestModel.description.ilike(f"%{search}%"))

            query = query.order_by(order_by).offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            orm_requests = result.scalars().all()

        # 4. Преобразуем в ответ
        domain_requests = self.mapper.to_domain_list(orm_requests)
        requests = [self.mapper.domain_to_response(r) for r in domain_requests]

        return requests, total

    async def create(self, request_data: RequestCreate) -> RequestResponse:
        """Создать новую заявку"""
        # Проверяем автора
        author = await self.employee_service.get_by_id(request_data.author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автор с ID {request_data.author_id} не найден"
            )

        # Проверяем исполнителя
        if request_data.executor_id:
            executor = await self.employee_service.get_by_id(request_data.executor_id)
            if not executor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Исполнитель с ID {request_data.executor_id} не найден"
                )

        # Проверяем дедлайн
        if request_data.deadline.replace(tzinfo=None) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Срок выполнения не может быть в прошлом"
            )

        # Генерируем номер
        number = await self.repository.get_next_number()

        # Создаём доменную сущность
        domain_request = Request(
            author_id=request_data.author_id,
            executor_id=request_data.executor_id,
            description=request_data.description,
            deadline=request_data.deadline.replace(tzinfo=None),
            number=number,
            status=RequestStatus.NEW
        )

        # Сохраняем в БД
        created_orm = await self.repository.create(
            number=domain_request.number,
            author_id=domain_request.author_id,
            executor_id=domain_request.executor_id,
            description=domain_request.description,
            deadline=domain_request.deadline,
            status=domain_request.status
        )

        domain_request.id = created_orm.id
        domain_request.created_at = created_orm.created_at

        return self.mapper.domain_to_response(domain_request)

    async def update(
        self,
        request_id: int,
        request_data: RequestUpdate
    ) -> Optional[RequestResponse]:
        """Обновить заявку"""
        existing = await self.repository.get_by_id(request_id)
        if not existing:
            return None

        if existing.status == RequestStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя изменять выполненную заявку"
            )

        update_data = {}

        if request_data.description is not None:
            update_data['description'] = request_data.description

        if request_data.deadline is not None:
            if request_data.deadline.replace(tzinfo=None) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Срок выполнения не может быть в прошлом"
                )
            update_data['deadline'] = request_data.deadline.replace(tzinfo=None)

        updated_orm = await self.repository.update(request_id, **update_data)
        if not updated_orm:
            return None

        domain_request = self.mapper.to_domain(updated_orm)
        return self.mapper.domain_to_response(domain_request)

    async def update_status(
        self,
        request_id: int,
        new_status: RequestStatus
    ) -> Optional[RequestResponse]:
        """Изменить статус заявки"""
        existing = await self.repository.get_by_id(request_id)
        if not existing:
            return None

        domain_request = self.mapper.to_domain(existing)

        try:
            domain_request.change_status(new_status)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        updated_orm = await self.repository.update(
            request_id,
            status=domain_request.status
        )

        if not updated_orm:
            return None

        domain_request = self.mapper.to_domain(updated_orm)
        return self.mapper.domain_to_response(domain_request)

    async def update_executor(
        self,
        request_id: int,
        executor_id: int
    ) -> Optional[RequestResponse]:
        """Сменить исполнителя"""
        existing = await self.repository.get_by_id(request_id)
        if not existing:
            return None

        executor = await self.employee_service.get_by_id(executor_id)
        if not executor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Исполнитель с ID {executor_id} не найден"
            )

        if existing.status == RequestStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя менять исполнителя у выполненной заявки"
            )

        domain_request = self.mapper.to_domain(existing)

        try:
            domain_request.change_executor(executor_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        updated_orm = await self.repository.update(
            request_id,
            executor_id=domain_request.executor_id
        )

        if not updated_orm:
            return None

        domain_request = self.mapper.to_domain(updated_orm)
        return self.mapper.domain_to_response(domain_request)

    async def delete(self, request_id: int) -> bool:
        """Удалить заявку"""
        existing = await self.repository.get_by_id(request_id)
        if not existing:
            return False

        if existing.status in [RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Нельзя удалить заявку в статусе '{existing.status.value}'"
            )

        return await self.repository.delete(request_id)

    async def get_overdue_for_executor(
        self,
        executor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestResponse]:
        """Получить просроченные заявки исполнителя"""
        executor = await self.employee_service.get_by_id(executor_id)
        if not executor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Исполнитель с ID {executor_id} не найден"
            )

        orm_requests = await self.repository.get_overdue_for_executor(
            executor_id=executor_id,
            skip=skip,
            limit=limit
        )

        domain_requests = self.mapper.to_domain_list(orm_requests)
        return [self.mapper.domain_to_response(r) for r in domain_requests]

    async def get_statistics(self) -> dict:
        """Получить статистику по заявкам"""
        return await self.repository.get_statistics()