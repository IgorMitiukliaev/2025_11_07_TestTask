from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from schemas.incident import (
    IncidentCreate,
    IncidentOut,
    IncidentStatusUpdate,
    IncidentDescriptionUpdate,
)
from schemas.errors import BaseErrorSchema
from core.enums import IncidentStatus, IncidentSource
from services.incident import IncidentService, IncidentNotFoundError
from core.unit_of_work import AbstractUnitOfWork
from core.dependencies import get_uow


router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_incident_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> IncidentService:
    return IncidentService(uow)


@router.post(
    "/",
    status_code=201,
    response_model=IncidentOut,
    responses={
        201: {"model": IncidentOut},
        400: {"model": BaseErrorSchema},
        500: {"model": BaseErrorSchema},
    },
)
async def create_incident(
    payload: IncidentCreate, service: IncidentService = Depends(get_incident_service)
) -> IncidentOut:
    """Создать новый инцидент"""
    try:
        return await service.create_incident(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/",
    response_model=List[IncidentOut],
    responses={
        200: {"model": List[IncidentOut]},
        500: {"model": BaseErrorSchema},
    },
)
async def list_incidents(
    status: IncidentStatus | None = Query(
        default=None, description="Фильтр по статусу"
    ),
    service: IncidentService = Depends(get_incident_service),
) -> List[IncidentOut]:
    """Получить список инцидентов с возможностью фильтрации по статусу"""
    try:
        if status:
            return await service.get_incidents_by_status(status)
        else:
            return await service.get_all_incidents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{incident_id}",
    response_model=IncidentOut,
    responses={
        200: {"model": IncidentOut},
        404: {"model": BaseErrorSchema},
        500: {"model": BaseErrorSchema},
    },
)
async def get_incident(
    incident_id: UUID, service: IncidentService = Depends(get_incident_service)
) -> IncidentOut:
    """Получить инцидент по ID"""
    try:
        return await service.get_incident_by_id(incident_id)
    except IncidentNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Incident with id {incident_id} not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/{incident_id}/status",
    response_model=IncidentOut,
    responses={
        200: {"model": IncidentOut},
        400: {"model": BaseErrorSchema},
        404: {"model": BaseErrorSchema},
        500: {"model": BaseErrorSchema},
    },
)
async def update_incident_status(
    incident_id: UUID,
    payload: IncidentStatusUpdate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentOut:
    """Обновить статус инцидента"""
    try:
        return await service.update_incident_status(incident_id, payload)
    except IncidentNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Incident with id {incident_id} not found"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/{incident_id}/description",
    response_model=IncidentOut,
    responses={
        200: {"model": IncidentOut},
        400: {"model": BaseErrorSchema},
        404: {"model": BaseErrorSchema},
        500: {"model": BaseErrorSchema},
    },
)
async def update_incident_description(
    incident_id: UUID,
    update_data: IncidentDescriptionUpdate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentOut:
    """Обновить описание инцидента"""
    try:
        return await service.update_incident_description(
            incident_id, update_data.new_description
        )
    except IncidentNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Incident with id {incident_id} not found"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{incident_id}",
    responses={
        204: {"description": "Incident deleted successfully"},
        404: {"model": BaseErrorSchema},
        400: {"model": BaseErrorSchema},
        500: {"model": BaseErrorSchema},
    },
)
async def delete_incident(
    incident_id: UUID, service: IncidentService = Depends(get_incident_service)
):
    """Удалить инцидент (только для решенных или отмененных)"""
    try:
        success = await service.delete_incident(incident_id)
        if success:
            return {"detail": "Incident deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete incident")
    except IncidentNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Incident with id {incident_id} not found"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
