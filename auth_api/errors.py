"""Logging y manejo centralizado de errores.

- configure_logging(): formato común de logs; nivel desde LOG_LEVEL (.env).
- register_error_handlers(app): convierte errores de base de datos en respuestas HTTP
  claras, registra cada petición (método, ruta, código, duración) y captura cualquier
  error no previsto para que el cliente reciba un JSON 500 y no una traza de Python.
"""
import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, SQLAlchemyError

logger = logging.getLogger("app")


def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
    )


def _error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_error_handlers(app: FastAPI) -> None:
    # Errores de base de datos. Se registran en el log completos, pero al cliente solo le llega
    # un mensaje genérico: nunca se exponen tablas, SQL ni datos internos.
    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        logger.warning("Violación de integridad en %s %s: %s", request.method, request.url.path, exc.orig)
        return _error(409, "La operación entra en conflicto con datos existentes")

    @app.exception_handler(DataError)
    async def data_error(request: Request, exc: DataError):
        logger.warning("Dato rechazado por la BD en %s %s: %s", request.method, request.url.path, exc.orig)
        return _error(422, "Uno de los valores no es válido para la base de datos (demasiado largo o fuera de rango)")

    @app.exception_handler(OperationalError)
    async def operational_error(request: Request, exc: OperationalError):
        logger.error("Base de datos no disponible en %s %s: %s", request.method, request.url.path, exc.orig)
        return _error(503, "La base de datos no está disponible. Intenta de nuevo en unos minutos")

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error(request: Request, exc: SQLAlchemyError):
        logger.exception("Error de base de datos en %s %s", request.method, request.url.path)
        return _error(500, "Error interno al acceder a la base de datos")

    # Middleware: registra cada petición y atrapa cualquier error no previsto.
    # Se registra ANTES que CORSMiddleware para quedar "por dentro" de él; así las respuestas
    # 500 también llevan las cabeceras CORS y el navegador puede leer el mensaje.
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Error no controlado en %s %s", request.method, request.url.path)
            response = _error(500, "Error interno del servidor")
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("%s %s -> %s (%.0f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
        return response
