from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
import uvicorn
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import router as api_router
from app.services.employee_service import EmployeeService
from app.services.request_service import RequestService
from app.services.report_service import ReportService
from app.core.dependencies import (
    get_employee_service,
    get_request_service,
    get_report_service
)
from app.schemas.request import RequestFilterParams
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.pagination import Pagination

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Запуск приложения...")
    try:
        await init_db()
        logger.info("✅ Таблицы созданы")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise
    yield
    logger.info("🛑 Остановка приложения...")


app = FastAPI(
    title=settings.app_name,
    description="Сервис управления сотрудниками и заявками",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Шаблоны
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def home(
        request: Request,
        employee_service: EmployeeService = Depends(get_employee_service),
        request_service: RequestService = Depends(get_request_service)
):
    """Главная страница"""
    try:
        # Получаем статистику
        stats = await request_service.get_statistics()

        # Получаем последние 10 заявок
        recent_requests = await request_service.get_filtered(
            filters=RequestFilterParams(),
            skip=0,
            limit=10
        )

        # Получаем последних 10 сотрудников
        employees = await employee_service.get_all(limit=10)

        # Получаем общее количество сотрудников
        all_employees = await employee_service.get_all(limit=1000000)
        employees_count = len(all_employees)

        by_status = stats.get('by_status', {})

        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": {
                "employees": employees_count,
                "requests": stats.get('total', 0),
                "new": by_status.get('new', 0),
                "in_progress": by_status.get('in_progress', 0),
                "completed": by_status.get('completed', 0),
                "overdue": stats.get('overdue_count', 0)
            },
            "recent_requests": recent_requests,
            "recent_employees": employees
        })
    except Exception as e:
        logger.error(f"❌ Ошибка на главной: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": {"employees": 0, "requests": 0, "new": 0, "in_progress": 0, "completed": 0, "overdue": 0},
            "recent_requests": [],
            "recent_employees": []
        })


@app.get("/employees", response_class=HTMLResponse)
async def employees_page(
        request: Request,
        department: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "full_name_asc",
        per_page: int = 10,
        page: int = 1,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """Страница списка сотрудников"""
    try:
        # Получаем данные через сервис
        employees, total, departments = await employee_service.get_filtered_paginated(
            department=department,
            search=search,
            sort=sort,
            per_page=per_page,
            page=page
        )

        # Формируем пагинацию
        pagination = Pagination(total, per_page, page)

        def url_for_page(page_num):
            params = []
            if department:
                params.append(f"department={department}")
            if search:
                params.append(f"search={search}")
            if sort:
                params.append(f"sort={sort}")
            if per_page:
                params.append(f"per_page={per_page}")
            params.append(f"page={page_num}")
            return f"/employees?{'&'.join(params)}"

        return templates.TemplateResponse("employees.html", {
            "request": request,
            "employees": employees,
            "departments": departments,
            "pagination": pagination.to_dict(url_for_page),
            "filters": {
                "department": department,
                "search": search,
                "sort": sort,
                "per_page": per_page,
                "page": page
            }
        })
    except Exception as e:
        logger.error(f"❌ Ошибка на странице сотрудников: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("employees.html", {
            "request": request,
            "employees": [],
            "departments": [],
            "pagination": None,
            "filters": {"department": "", "search": "", "sort": "full_name_asc", "per_page": 10}
        })


@app.get("/employees/create", response_class=HTMLResponse)
async def create_employee_page(request: Request):
    """Страница создания сотрудника"""
    return templates.TemplateResponse("employee_create.html", {"request": request})


@app.post("/employees")
async def create_employee_form(
        request: Request,
        full_name: str = Form(...),
        department: str = Form(...),
        position: str = Form(...),
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """Создание сотрудника из формы"""
    try:
        employee_data = EmployeeCreate(
            full_name=full_name,
            department=department,
            position=position
        )
        await employee_service.create(employee_data)
        return RedirectResponse("/employees", status_code=303)
    except Exception as e:
        logger.error(f"❌ Ошибка при создании сотрудника: {e}")
        return RedirectResponse(f"/employees/create?error={str(e)}", status_code=303)


@app.get("/employees/{employee_id}/edit", response_class=HTMLResponse)
async def edit_employee_page(
        request: Request,
        employee_id: int,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """Страница редактирования сотрудника"""
    try:
        employee = await employee_service.get_by_id(employee_id)
        if not employee:
            return templates.TemplateResponse("employee_edit.html", {
                "request": request,
                "error": "Сотрудник не найден",
                "employee": None
            })

        return templates.TemplateResponse("employee_edit.html", {
            "request": request,
            "employee": employee,
            "error": None
        })
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке сотрудника: {e}")
        return templates.TemplateResponse("employee_edit.html", {
            "request": request,
            "error": str(e),
            "employee": None
        })


@app.post("/employees/{employee_id}/edit")
async def update_employee_form(
        request: Request,
        employee_id: int,
        full_name: str = Form(...),
        department: str = Form(...),
        position: str = Form(...),
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """Обновление сотрудника из формы"""
    try:
        employee_data = EmployeeUpdate(
            full_name=full_name,
            department=department,
            position=position
        )

        updated = await employee_service.update(employee_id, employee_data)
        if not updated:
            return RedirectResponse(
                f"/employees/{employee_id}/edit?error=Сотрудник не найден",
                status_code=303
            )

        return RedirectResponse("/employees", status_code=303)
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении сотрудника: {e}")
        return RedirectResponse(
            f"/employees/{employee_id}/edit?error={str(e)}",
            status_code=303
        )


@app.get("/requests", response_class=HTMLResponse)
async def requests_page(
        request: Request,
        status: Optional[str] = None,
        sort: str = "created_at_desc",
        per_page: int = 10,
        page: int = 1,
        search: Optional[str] = None,
        request_service: RequestService = Depends(get_request_service)
):
    """Страница списка заявок"""
    try:
        # Получаем данные через сервис
        requests_list, total = await request_service.get_filtered_paginated(
            status=status,
            search=search,
            sort=sort,
            per_page=per_page,
            page=page
        )

        # Формируем пагинацию
        pagination = Pagination(total, per_page, page)

        def url_for_page(page_num):
            params = []
            if status:
                params.append(f"status={status}")
            if sort:
                params.append(f"sort={sort}")
            if per_page:
                params.append(f"per_page={per_page}")
            if search:
                params.append(f"search={search}")
            params.append(f"page={page_num}")
            return f"/requests?{'&'.join(params)}"

        return templates.TemplateResponse("requests.html", {
            "request": request,
            "requests": requests_list,
            "pagination": pagination.to_dict(url_for_page),
            "filters": {
                "status": status,
                "sort": sort,
                "per_page": per_page,
                "search": search,
                "page": page
            }
        })
    except Exception as e:
        logger.error(f"❌ Ошибка на странице заявок: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("requests.html", {
            "request": request,
            "requests": [],
            "pagination": None,
            "filters": {"status": "", "sort": "created_at_desc", "per_page": 10, "search": ""}
        })


@app.get("/requests/create", response_class=HTMLResponse)
async def create_request_page(
        request: Request,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """Страница создания заявки"""
    try:
        employees = await employee_service.get_all(limit=10000)
        return templates.TemplateResponse("request_create.html", {
            "request": request,
            "employees": employees
        })
    except Exception as e:
        logger.error(f"❌ Ошибка на странице создания: {e}")
        return templates.TemplateResponse("request_create.html", {
            "request": request,
            "employees": []
        })


@app.post("/requests")
async def create_request_form(
        request: Request,
        description: str = Form(...),
        author_id: int = Form(...),
        executor_id: int = Form(None),
        deadline: str = Form(...),
        request_service: RequestService = Depends(get_request_service)
):
    """Создание заявки из формы"""
    try:
        from app.schemas.request import RequestCreate

        deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))

        request_data = RequestCreate(
            description=description,
            author_id=author_id,
            executor_id=executor_id,
            deadline=deadline_dt
        )

        await request_service.create(request_data)
        return RedirectResponse("/requests", status_code=303)
    except Exception as e:
        logger.error(f"❌ Ошибка при создании заявки: {e}")
        return RedirectResponse(f"/requests/create?error={str(e)}", status_code=303)


@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(
        request: Request,
        executor_id: Optional[int] = None,
        report_service: ReportService = Depends(get_report_service)
):
    """Страница статистики"""
    try:
        stats = await report_service.get_statistics_with_filter(executor_id)
        employees = await report_service.get_all_employees()

        return templates.TemplateResponse("statistics.html", {
            "request": request,
            **stats,
            "employees": employees,
            "selected_executor": executor_id
        })
    except Exception as e:
        logger.error(f"❌ Ошибка на странице статистики: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("statistics.html", {
            "request": request,
            "total_requests": 0,
            "by_status": {},
            "overdue_count": 0,
            "by_executor": [],
            "employees": [],
            "selected_executor": None
        })


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "app": settings.app_name
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )