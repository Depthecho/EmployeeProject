from fastapi import APIRouter, Depends

from app.services.report_service import ReportService
from app.core.dependencies import get_report_service

router = APIRouter()


@router.get("/statistics")
async def get_statistics(
    service: ReportService = Depends(get_report_service)
):
    """
    Получение общей статистики по системе:
    - Количество заявок по статусам
    - Количество сотрудников по подразделениям
    - Другие агрегированные данные
    """
    return await service.get_statistics()