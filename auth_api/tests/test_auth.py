"""Tests de /auth/register y /auth/login."""
import jwt
import pytest
from sqlalchemy import select

from models import User
from security import ALGORITHM, SECRET_KEY


# ---------------------------------------------------------------- registro

def test_register_ok(client, new_user):
    res = client.post("/auth/register", json=new_user)

    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "María José"
    assert body["email"] == "maria@demo.com"
    assert "password" not in body  # la API nunca devuelve la contraseña


def test_register_guarda_hash_y_no_la_clave(client, db_session, new_user):
    client.post("/auth/register", json=new_user)

    with db_session() as db:
        user = db.scalar(select(User))
    assert user.password != new_user["password"]
    assert user.password.startswith("$2b$")  # formato bcrypt


def test_register_email_duplicado(client, new_user):
    client.post("/auth/register", json=new_user)
    res = client.post("/auth/register", json={**new_user, "email": "MARIA@demo.com"})

    assert res.status_code == 409  # el email se compara sin distinguir mayúsculas


def test_register_normaliza_espacios_y_email(client, new_user):
    res = client.post("/auth/register", json={**new_user, "name": "  Ana   Luz ", "email": "Ana@Demo.com"})

    assert res.status_code == 201
    assert res.json()["name"] == "Ana Luz"
    assert res.json()["email"] == "ana@demo.com"


@pytest.mark.parametrize("campo", ["name", "lastname"])
@pytest.mark.parametrize("valor", ["Juan2", "Ana_María", "P#rez", "@na", "Ana-Luz", "   "])
def test_register_nombre_solo_letras(client, new_user, campo, valor):
    res = client.post("/auth/register", json={**new_user, campo: valor})

    assert res.status_code == 422


@pytest.mark.parametrize("cambios", [
    {"email": "no-es-un-email"},
    {"password": "corta"},
    {"lastname": None},
])
def test_register_datos_invalidos(client, new_user, cambios):
    res = client.post("/auth/register", json={**new_user, **cambios})

    assert res.status_code == 422


# ---------------------------------------------------------------- login

def test_login_ok_devuelve_jwt_valido(client, new_user):
    user_id = client.post("/auth/register", json=new_user).json()["id"]

    res = client.post("/auth/login", json={"email": new_user["email"], "password": new_user["password"]})

    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["lastname"] == "Peña"
    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(user_id)
    assert payload["exp"] > payload["iat"]


def test_login_clave_incorrecta(client, new_user):
    client.post("/auth/register", json=new_user)

    res = client.post("/auth/login", json={"email": new_user["email"], "password": "OtraClave123"})

    assert res.status_code == 401
    assert res.json()["detail"] == "Credenciales inválidas"


def test_login_usuario_inexistente_mismo_mensaje(client):
    res = client.post("/auth/login", json={"email": "nadie@demo.com", "password": "Secreta123"})

    # Mismo código y mensaje que con clave incorrecta: no revela qué emails existen
    assert res.status_code == 401
    assert res.json()["detail"] == "Credenciales inválidas"
