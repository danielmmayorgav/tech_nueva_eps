"""Validación del token JWT emitido por la API de autenticación."""
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"

# Lee el encabezado "Authorization: Bearer <token>". Si falta, responde 401/403 automáticamente.
bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    try:
        # decode() verifica la firma y la expiración ("exp"); si algo falla lanza una excepción
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "El token expiró")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
