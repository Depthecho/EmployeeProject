from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    app_name: str = Field(default="EmployeeService")
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    database_url: str = Field(
        default="postgresql://postgres:Ex_di3212223!@db:5432/employee_db"
    )
    database_url_async: str = Field(
        default="postgresql+asyncpg://postgres:Ex_di3212223!@db:5432/employee_db"
    )
    db_pool_size: int = Field(default=20)
    db_max_overflow: int = Field(default=10)
    db_echo: bool = Field(default=False)

    secret_key: str = Field(default="change-me-in-production")

    test_employees_count: int = Field(default=1000)
    test_requests_count: int = Field(default=10000)
    test_batch_size: int = Field(default=1000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()