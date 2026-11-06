"""Hash de contraseñas (bcrypt) y emisión de tokens JWT."""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "120"))


def hash_password(password: str) -> str:
    # gensalt() genera una sal aleatoria: dos usuarios con la misma clave tienen hashes distintos
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user_id: int, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),   # "subject": a quién pertenece el token
        "email": email,
        "iat": now,            # emitido en
        "exp": now + timedelta(minutes=EXPIRE_MINUTES),  # expira en
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
