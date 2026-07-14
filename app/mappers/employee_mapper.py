from typing import Optional, List
from app.domain.entities.employee import Employee
from app.models.employee import EmployeeModel
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.mappers.base import BaseMapper


class EmployeeMapper(BaseMapper[Employee, EmployeeModel]):
    """
    Маппер для сотрудников.
    """

    def __init__(self):
        super().__init__(Employee, EmployeeModel)

    def to_domain(self, orm_obj: Optional[EmployeeModel]) -> Optional[Employee]:
        """
        Преобразование ORM-модели в доменную модель.
        Переопределяем для явного маппинга полей.
        """
        if orm_obj is None:
            return None

        return Employee(
            id=orm_obj.id,
            full_name=orm_obj.full_name,
            department=orm_obj.department,
            position=orm_obj.position,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at
        )

    def to_orm(self, domain_obj: Optional[Employee]) -> Optional[EmployeeModel]:
        """
        Преобразование доменной модели в ORM-модель.
        Переопределяем для явного маппинга полей.
        """
        if domain_obj is None:
            return None

        return EmployeeModel(
            id=domain_obj.id,
            full_name=domain_obj.full_name,
            department=domain_obj.department,
            position=domain_obj.position,
            created_at=domain_obj.created_at,
            updated_at=domain_obj.updated_at
        )

    def to_domain_list(self, orm_list: List[EmployeeModel]) -> List[Employee]:
        """
        Преобразование списка ORM-моделей в список доменных моделей.
        """
        return [self.to_domain(obj) for obj in orm_list] if orm_list else []


    def domain_to_response(self, domain: Employee) -> EmployeeResponse:
        """
        Преобразование доменной модели в Response-схему для API.
        """
        return EmployeeResponse(
            id=domain.id,
            full_name=domain.full_name,
            department=domain.department,
            position=domain.position,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )

    def create_to_domain(self, schema: EmployeeCreate) -> Employee:
        """
        Преобразование Create-схемы в доменную модель.
        Используется при создании нового сотрудника.
        """
        return Employee(
            full_name=schema.full_name,
            department=schema.department,
            position=schema.position
        )

    def update_to_domain(self, schema: EmployeeUpdate) -> Employee:
        """
        Преобразование Update-схемы в доменную модель.
        Используется при обновлении данных сотрудника.
        """
        return Employee(
            full_name=schema.full_name or "",
            department=schema.department or "",
            position=schema.position or ""
        )