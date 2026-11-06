"""Esquemas Pydantic: validan lo que entra y definen lo que sale de la API."""
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

# [^\W\d_] = cualquier letra Unicode (a-z, tildes, ñ, ü...): excluye números, "_" y símbolos.
# Palabras de letras separadas por un solo espacio: "María José", "De La Peña".
ONLY_LETTERS = re.compile(r"[^\W\d_]+(?: [^\W\d_]+)*")


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    lastname: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=72)  # bcrypt usa máx. 72 bytes

    @field_validator("name", "lastname")
    @classmethod
    def only_letters(cls, v: str) -> str:
        v = " ".join(v.split())  # quita espacios al inicio/fin y deja uno solo entre palabras
        if not ONLY_LETTERS.fullmatch(v):
            raise ValueError("solo se permiten letras y espacios (sin números ni caracteres especiales)")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    lastname: str
    email: EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
