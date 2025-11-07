"""
Конфигурация и создание FastAPI приложения
"""

from contextlib import asynccontextmanager
import traceback
from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware  # Убран - CORS не нужен
from fastapi.responses import JSONResponse

from api.routers import router as incidents_router
from core.config import app_config
from core.dependencies import settings
from services.incident import IncidentNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для приложения"""
    print("Starting Incident Management API...")
    print(f"Host: {app_config.POSTGRES_HOST}:{app_config.POSTGRES_PORT}")

    # Здесь можно добавить инициализацию БД при необходимости
    # await init_database()

    yield

    # Shutdown
    print("Shutting down Incident Management API...")
    print("Shutdown completed")


def setup_middleware(app: FastAPI) -> None:
    """Настройка middleware для приложения"""
    # cors_config = app_config.get_cors_config()
    # app.add_middleware(CORSMiddleware, **cors_config)
    pass


def setup_exception_handlers(app: FastAPI) -> None:
    """Настройка глобальных обработчиков исключений"""

    @app.exception_handler(IncidentNotFoundError)
    async def incident_not_found_handler(request, exc: IncidentNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )


def setup_routes(app: FastAPI) -> None:
    """Настройка маршрутов приложения"""

    # Основные эндпойнты приложения
    @app.get("/")
    async def root():
        return {
            "message": app_config.APP_NAME,
            "version": app_config.APP_VERSION,
            "status": "running",
        }

    @app.get("/health")
    async def health_check_endpoint():
        return {
            "status": "healthy",
            "application": {
                "name": app_config.APP_NAME,
                "version": app_config.APP_VERSION,
                "status": "running",
            },
        }

    app.include_router(incidents_router)


def create_app() -> FastAPI:
    app_metadata = app_config.get_app_metadata()
    app = FastAPI(**app_metadata, lifespan=lifespan)
    setup_middleware(app)
    setup_exception_handlers(app)
    setup_routes(app)

    return app


# Создание глобального экземпляра приложения
app = create_app()
