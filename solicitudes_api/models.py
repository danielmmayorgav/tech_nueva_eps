"""Modelos ORM de la API de solicitudes (tablas medications y requests)."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    is_pos: Mapped[bool] = mapped_column(Boolean)  # TINYINT 0/1 en MySQL -> False/True en Python


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    # user_id no se declara como ForeignKey aquí: la tabla users pertenece a la API de
    # autenticación. Esta API solo conoce el id que viene dentro del token JWT.
    user_id: Mapped[int]
    medication_id: Mapped[int] = mapped_column(ForeignKey("medications.id"))
    order_number: Mapped[Optional[str]] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    # server_default: SQLAlchemy omite la columna en el INSERT y MySQL pone current_timestamp()
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    medication: Mapped[Medication] = relationship(lazy="joined")
