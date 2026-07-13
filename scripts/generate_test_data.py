import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker

from app.core.database import AsyncSessionLocal
from app.models.employee import EmployeeModel
from app.models.request import RequestModel
from app.domain.enums.request_status import RequestStatus
from app.core.config import settings

fake = Faker("ru_RU")


async def generate_employees(count: int = 1000):
    """Генерировать сотрудников"""
    departments = ["IT", "HR", "Finance", "Marketing", "Sales", "R&D", "Legal", "Operations"]
    positions = ["Developer", "Manager", "Analyst", "Designer", "Tester", "Admin", "Director"]

    employees = []
    for _ in range(count):
        employee = EmployeeModel(
            full_name=fake.name(),
            department=random.choice(departments),
            position=random.choice(positions)
        )
        employees.append(employee)

    async with AsyncSessionLocal() as session:
        session.add_all(employees)
        await session.commit()
        print(f"✅ Создано {count} сотрудников")

    return employees


async def generate_requests(count: int = 1000000, employee_ids: list = None):
    """Генерировать заявки"""
    if not employee_ids:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(EmployeeModel.id))
            employee_ids = result.scalars().all()

    statuses = [RequestStatus.NEW, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]
    batch_size = settings.test_batch_size

    print(f"📝 Генерация {count} заявок...")

    for i in range(0, count, batch_size):
        batch = []
        for _ in range(min(batch_size, count - i)):
            created_at = fake.date_time_between(start_date="-1y", end_date="now")
            deadline = created_at + timedelta(days=random.randint(1, 30))
            status = random.choices(
                statuses,
                weights=[0.3, 0.4, 0.3]
            )[0]

            request = RequestModel(
                number=f"REQ-{i + _ + 1:06d}",
                created_at=created_at,
                author_id=random.choice(employee_ids),
                executor_id=random.choice(employee_ids) if random.random() > 0.2 else None,
                description=fake.text(max_nb_chars=200),
                deadline=deadline,
                status=status
            )
            batch.append(request)

        async with AsyncSessionLocal() as session:
            session.add_all(batch)
            await session.commit()

        print(f"   Создано {min(i + batch_size, count)} из {count} заявок")

    print(f"✅ Создано {count} заявок")


async def main():
    """Главная функция"""
    print("🚀 Начинаем генерацию тестовых данных...")

    # Генерируем сотрудников
    employees = await generate_employees(settings.test_employees_count)
    employee_ids = [e.id for e in employees]

    # Генерируем заявки
    await generate_requests(settings.test_requests_count, employee_ids)

    print("✅ Генерация завершена!")


if __name__ == "__main__":
    asyncio.run(main())