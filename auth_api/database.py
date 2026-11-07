"""Conexión a MySQL con SQLAlchemy.

Si DATABASE_URL está definido, se usa tal cual y se ignoran las variables DB_*
(lo usan los tests para trabajar con una base SQLite en memoria).
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # .env único en la raíz


def _build_url():
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    # URL.create escapa correctamente claves con caracteres especiales (@, :, /, #...)
    return URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
        query={"charset": "utf8mb4"},
    )


engine = create_engine(_build_url(), pool_pre_ping=True, pool_recycle=280)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
