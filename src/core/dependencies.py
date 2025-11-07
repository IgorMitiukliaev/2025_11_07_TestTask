"""
Зависимости для FastAPI эндпойнтов (только development режим)
"""

from sqlalchemy.ext.asyncio import AsyncSession

from core.unit_of_work import AbstractUnitOfWork, SQLAlchemyUnitOfWork
from core.config import app_config

settings = app_config

async def get_uow() -> AbstractUnitOfWork:
    """Dependency для получения Unit of Work"""
    from db.session import async_session

    session = async_session()
    return SQLAlchemyUnitOfWork(session)


# Настройки для development режима
class Settings:
    def __init__(self):
        self.environment = "development"
        self.database_url = app_config.DATABASE_URL
        self.debug = True  # Всегда включен в dev
        self.database_schema = app_config.POSTGRES_SCHEMA
        self.echo_sql = True  # Всегда включено в dev


settings = Settings()
