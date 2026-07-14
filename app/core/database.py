from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

Base = declarative_base()

# Создание асинхронного движка для подключения к БД
engine = create_async_engine(
    settings.database_url_async,
    echo=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
)

# Фабрика сессий для работы с БД
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор сессий для внедрения зависимости.
    Используется как Depends(get_session) в эндпоинтах.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Инициализация базы данных.
    """
    from app.models import employee

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)