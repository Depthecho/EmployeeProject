from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Класс конфигурации приложения.
    Загружает настройки из переменных окружения или файла .env
    """
    # Основные настройки приложения
    app_name: str = Field(default="EmployeeService", description="Название сервиса")
    debug: bool = Field(default=True, description="Режим отладки")
    host: str = Field(default="0.0.0.0", description="Хост для запуска сервера")
    port: int = Field(default=8000, description="Порт для запуска сервера")

    # Настройки подключения к базе данных
    database_url: str = Field(
        default="postgresql://postgres:Ex_di3212223!@db:5432/employee_db",
        description="URL для синхронного подключения к БД"
    )
    database_url_async: str = Field(
        default="postgresql+asyncpg://postgres:Ex_di3212223!@db:5432/employee_db",
        description="URL для асинхронного подключения к БД"
    )
    db_pool_size: int = Field(default=20, description="Размер пула соединений")
    db_max_overflow: int = Field(default=10, description="Максимальное переполнение пула")
    db_echo: bool = Field(default=False, description="Логирование SQL-запросов")

    # Настройки безопасности
    secret_key: str = Field(default="change-me-in-production", description="Секретный ключ для JWT")

    # Настройки для тестовых данных
    test_employees_count: int = Field(default=1000, description="Количество тестовых сотрудников")
    test_requests_count: int = Field(default=1000000, description="Количество тестовых заявок")
    test_batch_size: int = Field(default=1000, description="Размер батча для вставки тестовых данных")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()