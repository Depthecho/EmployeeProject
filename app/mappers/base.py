from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy import inspect

DomainEntity = TypeVar('DomainEntity')
ORMEntity = TypeVar('ORMEntity')


class BaseMapper(Generic[DomainEntity, ORMEntity]):

    def __init__(self, domain_class: Type[DomainEntity], orm_class: Type[ORMEntity]):
        self.domain_class = domain_class
        self.orm_class = orm_class

    def to_domain(self, orm_obj: Optional[ORMEntity]) -> Optional[DomainEntity]:
        if orm_obj is None:
            return None

        orm_fields = {c.key for c in inspect(orm_obj).mapper.column_attrs}

        data = {}
        for field in orm_fields:
            if hasattr(orm_obj, field):
                data[field] = getattr(orm_obj, field)

        return self.domain_class(**data)

    def to_orm(self, domain_obj: Optional[DomainEntity]) -> Optional[ORMEntity]:
        if domain_obj is None:
            return None

        domain_fields = domain_obj.__dataclass_fields__.keys() if hasattr(domain_obj, '__dataclass_fields__') else []

        data = {}
        for field in domain_fields:
            if hasattr(domain_obj, field):
                value = getattr(domain_obj, field)
                if value is not None:
                    data[field] = value

        return self.orm_class(**data)

    def to_domain_list(self, orm_list: List[ORMEntity]) -> List[DomainEntity]:
        return [self.to_domain(obj) for obj in orm_list] if orm_list else []

    def to_orm_list(self, domain_list: List[DomainEntity]) -> List[ORMEntity]:
        return [self.to_orm(obj) for obj in domain_list] if domain_list else []