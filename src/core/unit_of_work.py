from abc import ABC, abstractmethod
from typing import AsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.abstract_incident import AbstractIncidentRepository


class AbstractUnitOfWork(ABC):
    """Абстрактный интерфейс Unit of Work"""

    incidents: AbstractIncidentRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """Реализация Unit of Work для SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        from repositories.incident import IncidentRepository

        self.incidents = IncidentRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        """Коммит транзакции"""
        await self.session.commit()

    async def rollback(self):
        """Откат транзакции"""
        await self.session.rollback()
