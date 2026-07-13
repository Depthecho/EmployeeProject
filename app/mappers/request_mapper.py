from typing import Optional, List
from datetime import datetime

from app.domain.entities.request import Request
from app.domain.enums.request_status import RequestStatus
from app.models.request import RequestModel
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse
from app.mappers.base import BaseMapper


class RequestMapper(BaseMapper[Request, RequestModel]):

    def __init__(self):
        super().__init__(Request, RequestModel)

    def to_domain(self, orm_obj: Optional[RequestModel]) -> Optional[Request]:
        if orm_obj is None:
            return None

        return Request(
            id=orm_obj.id,
            number=orm_obj.number,
            created_at=orm_obj.created_at,
            author_id=orm_obj.author_id,
            executor_id=orm_obj.executor_id,
            description=orm_obj.description,
            deadline=orm_obj.deadline,
            status=orm_obj.status
        )

    def to_orm(self, domain_obj: Optional[Request]) -> Optional[RequestModel]:
        if domain_obj is None:
            return None

        return RequestModel(
            id=domain_obj.id,
            number=domain_obj.number,
            created_at=domain_obj.created_at,
            author_id=domain_obj.author_id,
            executor_id=domain_obj.executor_id,
            description=domain_obj.description,
            deadline=domain_obj.deadline,
            status=domain_obj.status
        )

    def to_domain_list(self, orm_list: List[RequestModel]) -> List[Request]:
        return [self.to_domain(obj) for obj in orm_list] if orm_list else []

    def domain_to_response(self, domain: Request) -> RequestResponse:
        return RequestResponse(
            id=domain.id,
            number=domain.number,
            created_at=domain.created_at,
            author_id=domain.author_id,
            executor_id=domain.executor_id,
            description=domain.description,
            deadline=domain.deadline,
            status=domain.status
        )

    def create_to_domain(self, schema: RequestCreate) -> Request:
        return Request(
            author_id=schema.author_id,
            executor_id=schema.executor_id,
            description=schema.description,
            deadline=schema.deadline.replace(tzinfo=None),
            number="",
            status=RequestStatus.NEW
        )

    def update_to_domain(self, schema: RequestUpdate) -> Request:
        return Request(
            description=schema.description or "",
            deadline=schema.deadline.replace(tzinfo=None) if schema.deadline else datetime.utcnow()
        )