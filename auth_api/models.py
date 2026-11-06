"""Modelos ORM: cada clase representa una tabla de tech_nueva_eps."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, FetchedValue, String, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    lastname: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))  # guarda el HASH bcrypt, no la clave
    # Las fechas las llena MySQL (DEFAULT / ON UPDATE current_timestamp()). server_default le
    # dice a SQLAlchemy que NO envíe NULL en el INSERT, para que se aplique el DEFAULT de la BD.
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_onupdate=FetchedValue())
