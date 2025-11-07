from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from repositories.abstract_incident import AbstractIncidentRepository
from models.incident import Incident
from core.enums import IncidentStatus, IncidentSource


class MockIncidentRepository(AbstractIncidentRepository):
    """Mock-реализация репозитория для тестирования"""
    
    def __init__(self):
        self._incidents: dict[UUID, Incident] = {}

    async def get_incident_by_id(self, incident_id: UUID) -> Optional[Incident]:
        """Получить инцидент по ID"""
        return self._incidents.get(incident_id)

    async def get_all_incidents(self) -> List[Incident]:
        """Получить все инциденты"""
        return list(self._incidents.values())

    async def get_incidents_by_status(self, status: IncidentStatus) -> List[Incident]:
        """Получить инциденты по статусу"""
        return [
            incident for incident in self._incidents.values() 
            if incident.status == status.value
        ]

    async def create_incident(
        self, 
        description: str, 
        status: IncidentStatus = IncidentStatus.OPEN,
        source: IncidentSource = IncidentSource.OPERATOR
    ) -> Incident:
        """Создать новый инцидент"""
        incident_id = uuid4()
        
        # Создаем mock объект с нужными атрибутами
        incident = type('MockIncident', (), {
            'id': incident_id,
            'description': description,
            'status': status.value,
            'source': source.value,
            'created_at': datetime.now(timezone.utc)
        })()
        
        self._incidents[incident_id] = incident
        return incident

    async def update_incident(self, incident_id: UUID, **update_data) -> Optional[Incident]:
        """Обновить инцидент"""
        incident = self._incidents.get(incident_id)
        if not incident:
            return None

        # Обновляем атрибуты
        for field, value in update_data.items():
            if hasattr(incident, field):
                setattr(incident, field, value)

        return incident

    async def delete_incident(self, incident_id: UUID) -> bool:
        """Удалить инцидент"""
        if incident_id in self._incidents:
            del self._incidents[incident_id]
            return True
        return False

    async def update_incident_status(self, incident_id: UUID, status: IncidentStatus) -> Optional[Incident]:
        """Обновить статус инцидента"""
        return await self.update_incident(incident_id, status=status.value)

    # Дополнительные методы для тестирования
    def clear(self):
        """Очистить все данные"""
        self._incidents.clear()

    def add_incident(self, incident: Incident):
        """Добавить инцидент напрямую (для setup тестов)"""
        self._incidents[incident.id] = incident

    def get_count(self) -> int:
        """Получить количество инцидентов"""
        return len(self._incidents)