from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import EmployeeService
from app.core.dependencies import get_employee_service

router = APIRouter()


@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    # Параметры фильтрации и пагинации
    department: Optional[str] = Query(None, description="Фильтр по подразделению"),
    search: Optional[str] = Query(None, description="Поиск по ФИО"),
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    service: EmployeeService = Depends(get_employee_service)
):
    """Получение списка всех сотрудников с фильтрацией и пагинацией"""
    employees = await service.get_all(
        department=department,
        search=search,
        skip=skip,
        limit=limit
    )
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service)
):
    """Получение сотрудника по ID"""
    employee = await service.get_by_id(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return employee


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service)
):
    """Создание нового сотрудника"""
    return await service.create(employee_data)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service)
):
    """Обновление данных сотрудника (частичное)"""
    employee = await service.update(employee_id, employee_data)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service)
):
    """Удаление сотрудника по ID"""
    deleted = await service.delete(employee_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return None


@router.get("/statistics")
async def get_statistics(
    service: EmployeeService = Depends(get_employee_service)
):
    """Получение статистики по сотрудникам (количество по подразделениям и т.д.)"""
    return await service.get_statistics()