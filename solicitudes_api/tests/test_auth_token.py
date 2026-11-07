"""Los endpoints solo responden a usuarios con un JWT válido."""
import pytest

from tests.conftest import auth, make_token

ENDPOINTS = [("get", "/medications"), ("get", "/requests"), ("post", "/requests")]


@pytest.mark.parametrize("method, path", ENDPOINTS)
def test_sin_token_rechaza(client, method, path):
    res = getattr(client, method)(path)

    assert res.status_code == 403


@pytest.mark.parametrize("method, path", ENDPOINTS)
@pytest.mark.parametrize("token", [
    "no-es-un-jwt",
    make_token(1, secret="otra-clave-distinta"),  # firmado por alguien que no conoce SECRET_KEY
])
def test_token_invalido_rechaza(client, method, path, token):
    res = getattr(client, method)(path, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401
    assert res.json()["detail"] == "Token inválido"


def test_token_expirado_rechaza(client):
    res = client.get("/requests", headers={"Authorization": f"Bearer {make_token(1, minutes=-1)}"})

    assert res.status_code == 401
    assert res.json()["detail"] == "El token expiró"


def test_listar_medicamentos(client):
    res = client.get("/medications", headers=auth())

    assert res.status_code == 200
    assert [(m["name"], m["is_pos"]) for m in res.json()] == [
        ("Acetaminofén 500 mg", True),
        ("Adalimumab 40 mg", False),
    ]
