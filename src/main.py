"""
Точка входа для запуска Incident Management API (development режим)
"""

import uvicorn
from core.config import app_config


def main():
    uvicorn_config = app_config.get_uvicorn_config()
    print(f"Starting server on {uvicorn_config['host']}:{uvicorn_config['port']}")
    print(f"API docs: http://{uvicorn_config['host']}:{uvicorn_config['port']}/docs")

    uvicorn.run("core.app:app", **uvicorn_config)  # Импорт приложения из core.app


if __name__ == "__main__":
    main()
