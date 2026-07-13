from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestResponse,
    RequestStatusUpdate,
    RequestExecutorUpdate,
    RequestFilterParams
)
from app.domain.enums.request_status import RequestStatus
from app.services.request_service import RequestService
from app.core.dependencies import get_request_service

router = APIRouter()


@router.get("/", response_model=List[RequestResponse])
async def get_requests(
    status: Optional[RequestStatus] = Query(None, description="Фильтр по статусу"),
    executor_id: Optional[int] = Query(None, description="Фильтр по исполнителю"),
    author_id: Optional[int] = Query(None, description="Фильтр по автору"),
    department: Optional[str] = Query(None, description="Фильтр по подразделению исполнителя"),
    overdue_only: bool = Query(False, description="Только просроченные"),
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    service: RequestService = Depends(get_request_service)
):
    filters = RequestFilterParams(
        status=status,
        executor_id=executor_id,
        author_id=author_id,
        department=department,
        overdue_only=overdue_only
    )
    requests = await service.get_filtered(filters, skip=skip, limit=limit)
    return requests


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: int,
    service: RequestService = Depends(get_request_service)
):
    request_obj = await service.get_by_id(request_id)
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )
    return request_obj


@router.post("/", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: RequestCreate,
    service: RequestService = Depends(get_request_service)
):
    return await service.create(request_data)


@router.patch("/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: int,
    request_data: RequestUpdate,
    service: RequestService = Depends(get_request_service)
):
    request_obj = await service.update(request_id, request_data)
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )
    return request_obj


@router.patch("/{request_id}/status", response_model=RequestResponse)
async def update_request_status(
    request_id: int,
    status_update: RequestStatusUpdate,
    service: RequestService = Depends(get_request_service)
):
    request_obj = await service.update_status(request_id, status_update.new_status)
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )
    return request_obj


@router.patch("/{request_id}/executor", response_model=RequestResponse)
async def update_request_executor(
    request_id: int,
    executor_update: RequestExecutorUpdate,
    service: RequestService = Depends(get_request_service)
):
    request_obj = await service.update_executor(request_id, executor_update.executor_id)
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )
    return request_obj


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: int,
    service: RequestService = Depends(get_request_service)
):
    deleted = await service.delete(request_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )
    return None


@router.get("/executor/{executor_id}/overdue", response_model=List[RequestResponse])
async def get_overdue_requests_for_executor(
    executor_id: int,
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    service: RequestService = Depends(get_request_service)
):
    return await service.get_overdue_for_executor(executor_id, skip=skip, limit=limit)