import pytest
from uuid import uuid4
from datetime import datetime
from typing import List
from unittest.mock import MagicMock, AsyncMock
from services.incident import IncidentService, IncidentNotFoundError
from schemas.incident import IncidentCreate, IncidentStatusUpdate
from core.enums import IncidentStatus, IncidentSource


def create_mock_incident(incident_id: str = None, description: str = "Test incident", 
                        status: IncidentStatus = IncidentStatus.OPEN, 
                        source: IncidentSource = IncidentSource.OPERATOR,
                        created_at: datetime = None) -> MagicMock:
    """Helper function to create properly configured mock incident"""
    mock_incident = MagicMock()
    mock_incident.id = incident_id or uuid4()
    mock_incident.description = description
    mock_incident.status = status
    mock_incident.source = source
    mock_incident.created_at = created_at or datetime.now()
    return mock_incident


class MockUnitOfWork:
    """Mock Unit of Work для тестирования"""

    def __init__(self):
        self.incidents = MagicMock()
        # Сделаем методы репозитория async
        self.incidents.create_incident = AsyncMock()
        self.incidents.get_incident_by_id = AsyncMock()
        self.incidents.get_all_incidents = AsyncMock()
        self.incidents.get_incidents_by_status = AsyncMock()
        self.incidents.update_incident_status = AsyncMock()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rolled_back = True
        else:
            self.committed = True

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True

    def reset(self):
        """Сброс состояния для тестов"""
        self.committed = False
        self.rolled_back = False


class TestIncidentService:
    """Тесты для IncidentService с использованием Mock UoW"""

    @pytest.fixture
    def uow(self):
        """Fixture для создания mock UoW"""
        mock_uow = MockUnitOfWork()
        return mock_uow

    @pytest.fixture
    def service(self, uow):
        """Fixture для создания сервиса"""
        return IncidentService(uow)

    @pytest.mark.asyncio
    async def test_create_incident(self, service, uow):
        """Тест создания инцидента"""
        # Настройка mock
        incident_id = uuid4()
        created_at = datetime.now()
        mock_incident = MagicMock()
        mock_incident.id = incident_id
        mock_incident.description = "Test incident"
        mock_incident.status = IncidentStatus.OPEN
        mock_incident.source = IncidentSource.OPERATOR
        mock_incident.created_at = created_at
        uow.incidents.create_incident.return_value = mock_incident

        incident_data = IncidentCreate(
            description="Test incident", source=IncidentSource.OPERATOR
        )
        result = await service.create_incident(incident_data)

        assert result.id == incident_id
        assert result.description == "Test incident"
        assert result.status == IncidentStatus.OPEN
        assert result.source == IncidentSource.OPERATOR
        assert result.created_at == created_at
        uow.incidents.create_incident.assert_called_once_with(
            description="Test incident",
            source=IncidentSource.OPERATOR,
            status=IncidentStatus.OPEN
        )
        assert uow.committed

        assert result.description == "Test incident"
        assert result.status == IncidentStatus.OPEN
        assert result.source == IncidentSource.OPERATOR
        assert uow.committed == True
        uow.incidents.create_incident.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_incident_by_id_found(self, service, uow):
        """Тест получения существующего инцидента по ID"""
        incident_id = uuid4()
        mock_incident = create_mock_incident(incident_id=incident_id)
        uow.incidents.get_incident_by_id.return_value = mock_incident

        result = await service.get_incident_by_id(incident_id)


        assert result.id == incident_id
        assert result.description == "Test incident"
        assert result.status == IncidentStatus.OPEN
        assert result.source == IncidentSource.OPERATOR
        assert uow.committed
        uow.incidents.get_incident_by_id.assert_called_once_with(incident_id)

    @pytest.mark.asyncio
    async def test_get_incident_by_id_not_found(self, service, uow):
        """Тест получения несуществующего инцидента"""
        uow.incidents.get_incident_by_id.return_value = None
        non_existent_id = uuid4()

        with pytest.raises(IncidentNotFoundError) as exc_info:
            await service.get_incident_by_id(non_existent_id)

        assert str(non_existent_id) in str(exc_info.value)
        uow.incidents.get_incident_by_id.assert_called_once_with(non_existent_id)

    @pytest.mark.asyncio
    async def test_get_all_incidents(self, service, uow):
        """Тест получения всех инцидентов"""
        mock_incidents = [
            create_mock_incident(description="Incident 1"),
            create_mock_incident(description="Incident 2")
        ]
        uow.incidents.get_all_incidents.return_value = mock_incidents

        result = await service.get_all_incidents()

        assert len(result) == 2
        assert result[0].description == "Incident 1"
        assert result[1].description == "Incident 2"
        assert all(incident.status == IncidentStatus.OPEN for incident in result)
        assert all(incident.source == IncidentSource.OPERATOR for incident in result)
        assert uow.committed
        uow.incidents.get_all_incidents.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_incidents_by_status(self, service, uow):
        """Тест получения инцидентов по статусу"""
        mock_incidents = [
            create_mock_incident(description="Open Incident 1", status=IncidentStatus.OPEN),
            create_mock_incident(description="Open Incident 2", status=IncidentStatus.OPEN)
        ]
        uow.incidents.get_incidents_by_status.return_value = mock_incidents

        result = await service.get_incidents_by_status(IncidentStatus.OPEN)

        assert len(result) == 2
        assert all(incident.status == IncidentStatus.OPEN for incident in result)
        assert all(incident.source == IncidentSource.OPERATOR for incident in result)
        assert uow.committed
        uow.incidents.get_incidents_by_status.assert_called_once_with(IncidentStatus.OPEN)

    @pytest.mark.asyncio
    async def test_update_incident_status_valid(self, service, uow):
        """Тест обновления статуса инцидента с допустимым переходом"""
        incident_id = uuid4()
        mock_incident = create_mock_incident(
            incident_id=incident_id, 
            status=IncidentStatus.OPEN  # Начальный статус OPEN
        )
        updated_incident = create_mock_incident(
            incident_id=incident_id,
            status=IncidentStatus.IN_PROGRESS  # Обновленный статус
        )

        uow.incidents.get_incident_by_id.return_value = mock_incident
        uow.incidents.update_incident_status.return_value = updated_incident

        status_update = IncidentStatusUpdate(status=IncidentStatus.IN_PROGRESS)
        result = await service.update_incident_status(incident_id, status_update)

        assert result.id == incident_id
        assert result.status == IncidentStatus.IN_PROGRESS
        assert uow.committed
        uow.incidents.get_incident_by_id.assert_called_once_with(incident_id)
        uow.incidents.update_incident_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_incident_status_not_found(self, service, uow):
        """Тест обновления статуса несуществующего инцидента"""
        uow.incidents.get_incident_by_id.return_value = None
        incident_id = uuid4()

        status_update = IncidentStatusUpdate(status=IncidentStatus.IN_PROGRESS)
        with pytest.raises(IncidentNotFoundError):
            await service.update_incident_status(incident_id, status_update)

        uow.incidents.get_incident_by_id.assert_called_once_with(incident_id)
        uow.incidents.update_incident_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_status_transition(self, service, uow):
        """Тест недопустимого перехода статуса"""
        incident_id = uuid4()
        mock_incident = MagicMock()
        mock_incident.id = incident_id
        mock_incident.status = IncidentStatus.RESOLVED.value

        uow.incidents.get_incident_by_id.return_value = mock_incident

        status_update = IncidentStatusUpdate(status=IncidentStatus.OPEN)
        with pytest.raises(ValueError) as exc_info:
            await service.update_incident_status(incident_id, status_update)

        assert "Invalid status transition" in str(exc_info.value)
        uow.incidents.update_incident_status.assert_not_called()