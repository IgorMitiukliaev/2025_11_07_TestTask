# Incident Management API

REST API для управления инцидентами с использованием FastAPI и PostgreSQL.

## Описание

Приложение предоставляет CRUD операции для управления инцидентами с поддержкой статусов и валидации переходов между ними.

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **Alembic** - миграции базы данных
- **Docker** - контейнеризация
- **pytest** - тестирование

## Установка и запуск

### Требования

- Docker и Docker Compose

### Запуск с Docker

1. Клонируйте репозиторий
2. Перейдите в директорию `src`
3. Запустите сервисы:

```bash
docker-compose up -d
```

Приложение будет доступно по адресу: http://localhost:8000

Документация API: http://localhost:8000/swagger/

Документация redoc: http://localhost:8000/redoc/

## API Endpoints

### Инциденты

- `GET /` - информация о приложении
- `GET /health` - проверка здоровья сервиса
- `POST /incidents/` - создание инцидента
- `GET /incidents/` - получение всех инцидентов
- `GET /incidents/{id}` - получение инцидента по ID
- `PATCH /incidents/{incident_id}/status` - обновление статуса инцидента
- `PATCH /incidents/{incident_id}/description` - обновление описания инцидента
- `DELETE /incidents/{incident_id}` - удаление инцидента

### Статусы инцидентов

- `open` - открыт
- `in_progress` - в работе
- `waiting` - ожидание
- `resolved` - решен
- `cancelled` - отменен

### Правила переходов статусов

- `open` → `in_progress`, `cancelled`
- `in_progress` → `waiting`, `resolved`
- `waiting` → `in_progress`, `resolved`
- `resolved` → (финальный статус)
- `cancelled` → (финальный статус)

## Тестирование

### Запуск тестов

```bash
cd src
python -m pytest ../tests/ -v
```

### Покрытие кода

```
python -m pytest --cov=. --cov-report=html --cov-report=term-missing ../tests/
```

Отчет о покрытии будет доступен в директории `htmlcov/`.


### Проверка при помощи curl

* Получить основную информацию о приложении
```
curl -X GET http://localhost:8000/
```


* Создать новый инцидент с описанием и источником
```
curl -X POST http://localhost:8000/incidents/ -H "Content-Type: application/json" -d '{"description": "Тестовый инцидент", "source": "operator"}'
```

* Получить список всех инцидентов
```
curl -X GET http://localhost:8000/incidents/
```
* Обновить статус инцидента с UUID на 'in_progress'
```
curl -X PATCH http://localhost:8000/incidents/<UUID>/status -H "Content-Type: application/json" -d '{"status": "in_progress"}'
```

* Обновить описание инцидента с UUID
```
curl -X PATCH http://localhost:8000/incidents/<UUID>/description -H "Content-Type: application/json" -d '{"new_description": "new"}'
```

## Структура проекта

```
src/
├── api/routers.py          # API маршруты
├── core/
│   ├── app.py             # Конфигурация FastAPI приложения
│   ├── config.py          # Настройки приложения
│   ├── dependencies.py    # Зависимости FastAPI
│   └── unit_of_work.py    # Unit of Work паттерн
├── db/session.py          # Конфигурация базы данных
├── models/                # SQLAlchemy модели
├── repositories/          # Репозитории данных
├── schemas/               # Pydantic схемы
└── services/              # Бизнес-логика
tests/                      # Модульные тесты
docker-compose.yaml         # Конфигурация Docker Compose
```

## Переменные окружения

- `POSTGRES_HOST` - хост базы данных
- `POSTGRES_PORT` - порт базы данных
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь базы данных
- `POSTGRES_PASSWORD` - пароль пользователя
- `APP_PORT` - порт приложения
- `APP_HOST` - хост приложения

