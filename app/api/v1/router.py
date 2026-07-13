from fastapi import APIRouter

from app.api.v1.endpoints import employees, requests, reports

router = APIRouter()

router.include_router(
    employees.router,
    prefix="/employees",
    tags=["Сотрудники"]
)

router.include_router(
    requests.router,
    prefix="/requests",
    tags=["Заявки"]
)

router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Отчеты"]
)