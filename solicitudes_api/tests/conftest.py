"""Configuración común de los tests de la API de solicitudes.

Los tests NO usan MySQL ni el túnel SSH: corren contra SQLite en memoria, que se crea
vacío (con un catálogo pequeño de medicamentos) antes de cada test.
"""
import os
from datetime import datetime, timedelta, timezone

os.environ.update({
    "DATABASE_URL": "sqlite://",
    "SSH_HOST": "",
    "SECRET_KEY": "clave-solo-para-tests",
    "LOG_LEVEL": "WARNING",
})

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402
from models import Medication  # noqa: E402
from security import ALGORITHM, SECRET_KEY  # noqa: E402

POS_ID, NO_POS_ID = 1, 2


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    with TestingSession() as db:
        db.add_all([
            Medication(id=POS_ID, name="Acetaminofén 500 mg", is_pos=True),
            Medication(id=NO_POS_ID, name="Adalimumab 40 mg", is_pos=False),
        ])
        db.commit()
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

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_token(user_id: int, minutes: int = 30, secret: str = SECRET_KEY) -> str:
    """Genera un JWT igual al que emite la API de autenticación."""
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def auth(user_id: int = 1) -> dict:
    return {"Authorization": f"Bearer {make_token(user_id)}"}


@pytest.fixture()
def no_pos_data():
    return {
        "medication_id": NO_POS_ID,
        "order_number": "OR-123",
        "address": "Calle 10 # 8-50",
        "phone": "+57 313 201 1550",
        "email": "paciente@demo.com",
    }
