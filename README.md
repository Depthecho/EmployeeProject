# 📋 Система управления заявками сотрудников

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)](https://docker.com)

> Современная система для управления заявками сотрудников с полным CRUD, фильтрацией, пагинацией и красивым веб-интерфейсом.

---

## 📌 Оглавление

- [✨ Особенности](#-особенности)
- [🏗 Архитектура](#-архитектура)
- [🚀 Быстрый старт](#-быстрый-старт)
  - [🐳 Запуск через Docker (рекомендуется)](#-запуск-через-docker-рекомендуется)
  - [🖥 Запуск локально](#-запуск-локально)
- [📚 API Документация](#-api-документация)
- [💻 Веб-интерфейс](#-веб-интерфейс)
- [📊 Бизнес-логика](#-бизнес-логика)
- [⚡ Производительность](#-производительность)
- [🛠 Технологический стек](#-технологический-стек)
- [📁 Структура проекта](#-структура-проекта)

---

## ✨ Особенности

### 🔹 Сотрудники
- ✅ Полный CRUD (создание, чтение, обновление, удаление)
- ✅ Фильтрация по подразделению
- ✅ Поиск по ФИО
- ✅ Сортировка по нескольким полям
- ✅ Пагинация

### 🔹 Заявки
- ✅ Полный CRUD
- ✅ Бизнес-логика статусов (Новая → В работе → Выполнена)
- ✅ Фильтрация по статусу, исполнителю, автору, подразделению
- ✅ Поиск по описанию
- ✅ Сортировка по дате, дедлайну, номеру
- ✅ Просроченные заявки
- ✅ Пагинация

### 🔹 Отчётность
- ✅ Количество заявок по статусам
- ✅ Количество просроченных заявок
- ✅ Количество выполненных заявок по исполнителям
- ✅ Фильтр по исполнителю

### 🔹 Веб-интерфейс
- ✅ Тёмная футуристичная тема
- ✅ Адаптивный дизайн
- ✅ Неоновые акценты
- ✅ Интерактивные элементы
- ✅ Select2 с поиском для выбора сотрудников

### 🔹 API
- ✅ RESTful API
- ✅ Swagger документация (OpenAPI)
- ✅ Валидация данных через Pydantic
- ✅ Асинхронные запросы

---

## 🏗 Архитектура

Проект построен на **чистой архитектуре** с разделением на слои:

🎯 API Layer
(FastAPI эндпоинты)

🧠 Service Layer
(Бизнес-логика)

🔄 Repository Layer
(Доступ к данным)

🗄️ Database Layer
(PostgreSQL)



### Паттерны:
- **Repository** - абстракция доступа к данным
- **DataMapper** - преобразование между слоями
- **Dependency Injection** - внедрение зависимостей
- **Service Layer** - бизнес-логика

---

## 🚀 Быстрый старт

### 🐳 Запуск через Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourusername/employee-service.git
cd employee-service

# 2. Создать .env файл
cp .env.example .env

# 3. Запустить через Docker Compose
docker-compose up -d --build

# 4. Проверить что всё работает
docker-compose logs -f app



После запуска:

Веб-интерфейс: http://localhost:8000
API документация: http://localhost:8000/docs
Health check: http://localhost:8000/health
```

 Запуск локально

```commandline
# 1. Создать виртуальное окружение
python -m venv venv

# 2. Активировать виртуальное окружение
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл (скопировать из .env.example)
cp .env.example .env

# 5. Настроить PostgreSQL и обновить DATABASE_URL в .env

# 6. Запустить приложение
uvicorn app.main:app --reload

# 7. Открыть в браузере
# http://localhost:8000
```



💻 Веб-интерфейс
Главная страница
📊 Статистика заявок (Всего, Новые, В работе, Выполнено, Просрочено)

📋 Последние заявки

👥 Последние сотрудники


Сотрудники
📋 Список с пагинацией

🔍 Фильтр по подразделению

🔎 Поиск по ФИО

➕ Создание/редактирование

🗑 Удаление


Заявки
📋 Список с пагинацией

🔍 Фильтр по статусу

🔎 Поиск по описанию

📊 Сортировка (по дате, дедлайну, номеру)

➕ Создание заявки

🔄 Изменение статуса (Новая → В работе → Выполнена)

👤 Смена исполнителя


Статистика
📊 Количество по статусам с прогресс-барами

⏰ Просроченные заявки

👥 Топ исполнителей с медалями

🔍 Фильтр по конкретному исполнителю



```commandline
# Генерация 1000 сотрудников и 1 000 000 заявок
python scripts/generate_test_data.py
```

```commandline
-- Для заявок
CREATE INDEX idx_requests_executor_status_deadline ON requests(executor_id, status, deadline);
CREATE INDEX idx_requests_author_status ON requests(author_id, status);
CREATE INDEX idx_requests_status_deadline ON requests(status, deadline);
CREATE INDEX idx_requests_number ON requests(number);

-- Для сотрудников
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_full_name ON employees(full_name);

Результаты тестов:
📉 Без индексов: ~2-3 секунды
📈 С индексами: ~50-100 мс
```



📞 Контакты
По всем вопросам обращайтесь:

📧 Email: 51miha7@gmail.com

🐛 Баги и предложения: GitHub Issues