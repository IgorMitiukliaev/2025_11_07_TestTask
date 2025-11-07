from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.unit_of_work import AbstractUnitOfWork
from schemas.incident import IncidentCreate, IncidentOut, IncidentStatusUpdate
from models.incident import Incident
from core.enums import IncidentStatus, IncidentSource


class IncidentNotFoundError(Exception):
    """Исключение для случаев, когда инцидент не найден"""
    def __init__(self, incident_id: UUID):
        self.incident_id = incident_id
        super().__init__(f"Incident with id {incident_id} not found")


class IncidentService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_incident_by_id(self, incident_id: UUID) -> IncidentOut:
        """Получить инцидент по ID"""
        async with self.uow:
            incident = await self.uow.incidents.get_incident_by_id(incident_id)
            if not incident:
                raise IncidentNotFoundError(incident_id)
            return IncidentOut.model_validate(incident)

    async def get_all_incidents(self) -> List[IncidentOut]:
        """Получить все инциденты"""
        async with self.uow:
            incidents = await self.uow.incidents.get_all_incidents()
            return [IncidentOut.model_validate(incident) for incident in incidents]

    async def get_incidents_by_status(self, status: IncidentStatus) -> List[IncidentOut]:
        """Получить инциденты по статусу"""
        async with self.uow:
            incidents = await self.uow.incidents.get_incidents_by_status(status)
            return [IncidentOut.model_validate(incident) for incident in incidents]

    async def create_incident(self, incident_data: IncidentCreate) -> IncidentOut:
        """Создать новый инцидент"""
        async with self.uow:
            incident = await self.uow.incidents.create_incident(
                description=incident_data.description,
                source=incident_data.source,
                status=IncidentStatus.OPEN  # Новые инциденты всегда открыты
            )
            return IncidentOut.model_validate(incident)

    async def update_incident_status(self, incident_id: UUID, status_update: IncidentStatusUpdate) -> IncidentOut:
        """Обновить статус инцидента"""
        async with self.uow:
            # Проверяем существование инцидента
            existing_incident = await self.uow.incidents.get_incident_by_id(incident_id)
            if not existing_incident:
                raise IncidentNotFoundError(incident_id)

            # Проверяем валидность перехода статуса
            current_status = IncidentStatus(existing_incident.status)
            new_status = status_update.status
            
            if not self._is_valid_status_transition(current_status, new_status):
                raise ValueError(f"Invalid status transition from {current_status} to {new_status}")

            # Обновляем статус
            updated_incident = await self.uow.incidents.update_incident_status(incident_id, new_status)
            return IncidentOut.model_validate(updated_incident)

    async def delete_incident(self, incident_id: UUID) -> bool:
        """Удалить инцидент"""
        async with self.uow:
            # Проверяем существование инцидента
            existing_incident = await self.uow.incidents.get_incident_by_id(incident_id)
            if not existing_incident:
                raise IncidentNotFoundError(incident_id)

            # Проверяем, можно ли удалить инцидент (например, только отмененные или решенные)
            current_status = IncidentStatus(existing_incident.status)
            if current_status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]:
                raise ValueError(f"Cannot delete incident with status {current_status}. Only resolved or cancelled incidents can be deleted.")

            return await self.uow.incidents.delete_incident(incident_id)

    async def update_incident_description(self, incident_id: UUID, new_description: str) -> IncidentOut:
        """Обновить описание инцидента"""
        async with self.uow:
            # Проверяем существование инцидента
            existing_incident = await self.uow.incidents.get_incident_by_id(incident_id)
            if not existing_incident:
                raise IncidentNotFoundError(incident_id)

            # Проверяем, можно ли изменить описание (только для открытых инцидентов)
            current_status = IncidentStatus(existing_incident.status)
            if current_status in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]:
                raise ValueError(f"Cannot update description for incident with status {current_status}")

            # Обновляем описание
            updated_incident = await self.uow.incidents.update_incident(incident_id, description=new_description)
            return IncidentOut.model_validate(updated_incident)

    def _is_valid_status_transition(self, current_status: IncidentStatus, new_status: IncidentStatus) -> bool:
        """Проверить валидность перехода между статусами"""
        # Определяем разрешенные переходы
        valid_transitions = {
            IncidentStatus.OPEN: [IncidentStatus.IN_PROGRESS, IncidentStatus.CANCELLED],
            IncidentStatus.IN_PROGRESS: [IncidentStatus.WAITING, IncidentStatus.RESOLVED, IncidentStatus.CANCELLED],
            IncidentStatus.WAITING: [IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLVED, IncidentStatus.CANCELLED],
            IncidentStatus.RESOLVED: [],  # Решенные инциденты нельзя изменять
            IncidentStatus.CANCELLED: []  # Отмененные инциденты нельзя изменять
        }

        # Проверяем, разрешен ли переход
        allowed_statuses = valid_transitions.get(current_status, [])
        return new_status in allowed_statuses

