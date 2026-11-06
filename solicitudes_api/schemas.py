"""Esquemas Pydantic de la API de solicitudes."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class MedicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # permite crear el esquema desde un objeto ORM

    id: int
    name: str
    is_pos: bool


class RequestCreate(BaseModel):
    medication_id: int
    # Opcionales a nivel de esquema; la API los exige si el medicamento es NO POS
    order_number: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20, pattern=r"^[0-9+\-\s()]{7,20}$")
    email: Optional[EmailStr] = Field(None, max_length=100)

    @field_validator("order_number", "address", "phone", "email", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        """Convierte '' o '   ' en None para que 'obligatorio' signifique 'con contenido'."""
        if isinstance(v, str):
            return v.strip() or None
        return v


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medication: MedicationOut
    order_number: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    created_at: datetime


class Page(BaseModel):
    items: list[RequestOut]
    total: int
    page: int
    size: int
    pages: int
