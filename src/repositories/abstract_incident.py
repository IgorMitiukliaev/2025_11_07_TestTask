from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from models.incident import Incident
from core.enums import IncidentStatus, IncidentSource


class AbstractIncidentRepository(ABC):
    """Абстрактный интерфейс репозитория для работы с инцидентами"""

    @abstractmethod
    async def get_incident_by_id(self, incident_id: UUID) -> Optional[Incident]:
        """Получить инцидент по ID"""
        raise NotImplementedError

    @abstractmethod
    async def get_all_incidents(self) -> List[Incident]:
        """Получить все инциденты"""
        raise NotImplementedError

    @abstractmethod
    async def get_incidents_by_status(self, status: IncidentStatus) -> List[Incident]:
        """Получить инциденты по статусу"""
        raise NotImplementedError

    @abstractmethod
    async def create_incident(
        self, 
        description: str, 
        status: IncidentStatus = IncidentStatus.OPEN,
        source: IncidentSource = IncidentSource.OPERATOR
    ) -> Incident:
        """Создать новый инцидент"""
        raise NotImplementedError

    @abstractmethod
    async def update_incident(self, incident_id: UUID, **update_data) -> Optional[Incident]:
        """Обновить инцидент"""
        raise NotImplementedError

    @abstractmethod
    async def delete_incident(self, incident_id: UUID) -> bool:
        """Удалить инцидент"""
        raise NotImplementedError

    @abstractmethod
    async def update_incident_status(self, incident_id: UUID, status: IncidentStatus) -> Optional[Incident]:
        """Обновить статус инцидента"""
        raise NotImplementedError