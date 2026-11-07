"""Configuración común de los tests de la API de autenticación.

Los tests NO usan MySQL: corren contra SQLite en memoria, que se crea
vacío antes de cada test y se descarta al terminar. Así son rápidos, repetibles y no
ensucian la base real.
"""
import os

# Estas variables deben existir ANTES de importar la app. load_dotenv() no sobrescribe
# variables ya definidas, así que el .env real (MySQL) queda ignorado.
os.environ.update({
    "DATABASE_URL": "sqlite://",
    "SECRET_KEY": "clave-solo-para-tests",
    "LOG_LEVEL": "WARNING",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture()
def db_session():
    # StaticPool: una sola conexión compartida, necesaria para que la BD en memoria
    # sea la misma en el test y en la petición que procesa la API.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    yield TestingSession
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    # Inyección de dependencias: la API usará la BD de prueba en lugar de la real
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def new_user():
    return {"name": "María José", "lastname": "Peña", "email": "maria@demo.com", "password": "Secreta123"}
