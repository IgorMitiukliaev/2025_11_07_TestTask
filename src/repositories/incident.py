from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound
from models.incident import Incident
from core.enums import IncidentStatus, IncidentSource
from repositories.abstract_incident import AbstractIncidentRepository


class IncidentRepository(AbstractIncidentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_incident_by_id(self, incident_id: UUID) -> Optional[Incident]:
        """Получить инцидент по ID"""
        stmt = select(Incident).where(Incident.id == incident_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_incidents(self) -> List[Incident]:
        """Получить все инциденты"""
        stmt = select(Incident).order_by(Incident.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_incidents_by_status(self, status: IncidentStatus) -> List[Incident]:
        """Получить инциденты по статусу"""
        stmt = select(Incident).where(Incident.status == status.value).order_by(Incident.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_incident(
        self, 
        description: str, 
        status: IncidentStatus = IncidentStatus.OPEN,
        source: IncidentSource = IncidentSource.OPERATOR
    ) -> Incident:
        """Создать новый инцидент"""
        incident = Incident(
            description=description,
            status=status.value,
            source=source.value
        )
        self.session.add(incident)
        await self.session.flush()  # Используем flush вместо commit
        await self.session.refresh(incident)
        return incident

    async def update_incident(self, incident_id: UUID, **update_data) -> Optional[Incident]:
        """Обновить инцидент"""
        # Получаем инцидент для проверки существования
        incident = await self.get_incident_by_id(incident_id)
        if not incident:
            return None

        # Обновляем только переданные поля
        for field, value in update_data.items():
            if hasattr(incident, field):
                setattr(incident, field, value)

        await self.session.flush()  # Используем flush вместо commit
        await self.session.refresh(incident)
        return incident

    async def delete_incident(self, incident_id: UUID) -> bool:
        """Удалить инцидент"""
        incident = await self.get_incident_by_id(incident_id)
        if not incident:
            return False

        await self.session.delete(incident)
        await self.session.flush()  # Используем flush вместо commit
        return True

    async def update_incident_status(self, incident_id: UUID, status: IncidentStatus) -> Optional[Incident]:
        """Обновить статус инцидента"""
        return await self.update_incident(incident_id, status=status.value)
