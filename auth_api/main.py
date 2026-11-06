"""API de Autenticación  ->  uvicorn main:app --reload --port 8001"""
import logging
import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from errors import configure_logging, register_error_handlers

configure_logging()  # antes de importar database, para que el log del túnel SSH ya tenga formato

from database import get_db  # noqa: E402
from models import User  # noqa: E402
from schemas import LoginIn, TokenOut, UserCreate, UserOut  # noqa: E402
from security import create_token, hash_password, verify_password  # noqa: E402

logger = logging.getLogger("app.auth")

app = FastAPI(title="Auth API", version="1.0.0")

register_error_handlers(app)  # debe ir antes de CORSMiddleware (ver errors.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_out(user: User) -> UserOut:
    return UserOut(id=user.id, name=user.name, lastname=user.lastname, email=user.email)


@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "El email ya está registrado")

    user = User(
        name=data.name.strip(),
        lastname=data.lastname.strip(),
        email=email,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Usuario registrado id=%s", user.id)
    return to_out(user)


@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    # Mismo mensaje si no existe el usuario o si la clave es incorrecta (no revelar cuál falló)
    if not user or not verify_password(data.password, user.password):
        # Se registra para poder detectar intentos de fuerza bruta (nunca se loguea la contraseña)
        logger.warning("Login fallido para %s", data.email.lower())
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")

    logger.info("Login exitoso usuario id=%s", user.id)
    return TokenOut(access_token=create_token(user.id, user.email), user=to_out(user))


@app.get("/health")
def health():
    return {"status": "ok"}
