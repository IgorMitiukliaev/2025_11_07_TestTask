"""
Конфигурация базы данных и сессий SQLAlchemy для development режима
"""

import os
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from contextvars import ContextVar
from typing import AsyncGenerator
from core.config import app_config

DATABASE_URL = app_config.DATABASE_URL
POSTGRES_SCHEMA = app_config.POSTGRES_SCHEMA

# Создание движка базы данных для development
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=5,  # Меньший размер пула для dev
    max_overflow=10,  # Меньше дополнительных соединений для dev
    pool_timeout=30,  # Таймаут ожидания соединения
    pool_recycle=3600,  # Переиспользование соединений (1 час)
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_async_session():
    async with async_session() as session:
        yield session

# Конвенции именования для индексов и ограничений
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


# Базовый класс для моделей SQLAlchemy
Base = declarative_base(
    metadata=MetaData(
        schema=POSTGRES_SCHEMA if POSTGRES_SCHEMA != "public" else None,
        naming_convention=naming_convention,
    )
)

