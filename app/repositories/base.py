from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с CRUD-операциями для работы с БД.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Инициализация репозитория.

        Args:
            model: Класс ORM-модели
            session: Асинхронная сессия SQLAlchemy
        """
        self.model = model
        self.session = session

    # БАЗОВЫЕ CRUD-ОПЕРАЦИИ

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получение записи по ID"""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters
    ) -> List[ModelType]:
        """
        Получение списка записей с пагинацией и фильтрацией.

        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            **filters: Фильтры по полям (ключ=значение)
        """
        query = select(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """Создание новой записи"""
        instance = self.model(**kwargs)
        self.session.add(instance)

        try:
            await self.session.commit()
            await self.session.refresh(instance)
        except Exception as e:
            await self.session.rollback()
            raise

        return instance

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Обновление записи по ID.
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)

        try:
            await self.session.commit()
            await self.session.refresh(instance)
        except Exception as e:
            await self.session.rollback()
            raise

        return instance

    async def delete(self, id: int) -> bool:
        """
        Удаление записи по ID.
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.session.delete(instance)
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise

        return True

    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ

    async def count(self, **filters) -> int:
        """
        Подсчет количества записей с фильтрацией.
        """
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar()

    async def exists(self, **filters) -> bool:
        """Проверка существования записи по фильтрам"""
        count = await self.count(**filters)
        return count > 0

    async def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[ModelType, bool]:
        """
        Получение существующей записи или создание новой.

        Args:
            defaults: Дополнительные данные для создания (если запись не найдена)
            **kwargs: Критерии поиска
        """
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        instance = result.scalar_one_or_none()

        if instance:
            return instance, False

        # Создание новой записи
        create_data = {**kwargs}
        if defaults:
            create_data.update(defaults)
        instance = await self.create(**create_data)
        return instance, True