from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.request_repository import RequestRepository
from app.services.employee_service import EmployeeService
from app.services.request_service import RequestService
from app.services.report_service import ReportService
from app.mappers.employee_mapper import EmployeeMapper
from app.mappers.request_mapper import RequestMapper
from app.validators.request_validator import RequestValidator


async def get_employee_repository(
    session: AsyncSession = Depends(get_session)
) -> EmployeeRepository:
    return EmployeeRepository(session)


async def get_request_repository(
    session: AsyncSession = Depends(get_session)
) -> RequestRepository:
    return RequestRepository(session)


def get_employee_mapper() -> EmployeeMapper:
    return EmployeeMapper()


def get_request_mapper() -> RequestMapper:
    return RequestMapper()


def get_request_validator() -> RequestValidator:
    return RequestValidator()


async def get_employee_service(
    repository: EmployeeRepository = Depends(get_employee_repository),
    mapper: EmployeeMapper = Depends(get_employee_mapper),
) -> EmployeeService:
    return EmployeeService(repository, mapper)


async def get_request_service(
    repository: RequestRepository = Depends(get_request_repository),
    mapper: RequestMapper = Depends(get_request_mapper),
    employee_service: EmployeeService = Depends(get_employee_service),
    employee_repository: EmployeeRepository = Depends(get_employee_repository),
) -> RequestService:
    return RequestService(
        repository=repository,
        mapper=mapper,
        employee_service=employee_service,
        employee_repository=employee_repository
    )


async def get_report_service(
    request_repository: RequestRepository = Depends(get_request_repository),
    employee_repository: EmployeeRepository = Depends(get_employee_repository),
) -> ReportService:
    return ReportService(request_repository, employee_repository)