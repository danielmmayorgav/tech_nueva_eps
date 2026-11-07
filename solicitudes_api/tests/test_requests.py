"""Creación de solicitudes (regla POS / NO POS) y listado paginado."""
import pytest

from tests.conftest import NO_POS_ID, POS_ID, auth


# ---------------------------------------------------------------- crear: POS

def test_crear_pos_sin_datos_adicionales(client):
    res = client.post("/requests", json={"medication_id": POS_ID}, headers=auth())

    assert res.status_code == 201
    body = res.json()
    assert body["medication"]["is_pos"] is True
    assert body["created_at"]  # lo pone la base de datos


def test_crear_pos_descarta_datos_adicionales(client, no_pos_data):
    res = client.post("/requests", json={**no_pos_data, "medication_id": POS_ID}, headers=auth())

    assert res.status_code == 201
    body = res.json()
    assert body["order_number"] is None and body["address"] is None
    assert body["phone"] is None and body["email"] is None


# ---------------------------------------------------------------- crear: NO POS

def test_crear_no_pos_completo(client, no_pos_data):
    res = client.post("/requests", json=no_pos_data, headers=auth())

    assert res.status_code == 201
    body = res.json()
    assert body["order_number"] == "OR-123"
    assert body["phone"] == "+57 313 201 1550"  # se guarda como texto, sin perder el +57


@pytest.mark.parametrize("campo, etiqueta", [
    ("order_number", "número de orden"),
    ("address", "dirección"),
    ("phone", "teléfono"),
    ("email", "correo electrónico"),
])
@pytest.mark.parametrize("valor", [None, "", "    "])
def test_crear_no_pos_campo_obligatorio(client, no_pos_data, campo, etiqueta, valor):
    res = client.post("/requests", json={**no_pos_data, campo: valor}, headers=auth())

    assert res.status_code == 422
    assert etiqueta in res.json()["detail"]


@pytest.mark.parametrize("cambios", [
    {"phone": "abc1234567"},
    {"phone": "123"},
    {"email": "no-es-email"},
    {"address": "x" * 101},
])
def test_crear_no_pos_formato_invalido(client, no_pos_data, cambios):
    res = client.post("/requests", json={**no_pos_data, **cambios}, headers=auth())

    assert res.status_code == 422


def test_crear_medicamento_inexistente(client):
    res = client.post("/requests", json={"medication_id": 999}, headers=auth())

    assert res.status_code == 404


def test_crear_ignora_user_id_del_body(client):
    """El dueño de la solicitud sale del token, nunca de lo que envía el cliente."""
    client.post("/requests", json={"medication_id": POS_ID, "user_id": 2}, headers=auth(user_id=1))

    assert client.get("/requests", headers=auth(user_id=1)).json()["total"] == 1
    assert client.get("/requests", headers=auth(user_id=2)).json()["total"] == 0


# ---------------------------------------------------------------- listado paginado

def _crear(client, n, user_id=1):
    return [
        client.post("/requests", json={"medication_id": POS_ID}, headers=auth(user_id)).json()["id"]
        for _ in range(n)
    ]


def test_listado_vacio(client):
    res = client.get("/requests", headers=auth())

    assert res.status_code == 200
    assert res.json() == {"items": [], "total": 0, "page": 1, "size": 10, "pages": 1}


def test_paginacion(client):
    ids = _crear(client, 12)

    p1 = client.get("/requests?page=1&size=5", headers=auth()).json()
    p3 = client.get("/requests?page=3&size=5", headers=auth()).json()

    newest_first = ids[::-1]
    assert (p1["total"], p1["pages"]) == (12, 3)
    assert [i["id"] for i in p1["items"]] == newest_first[:5]    # más recientes primero
    assert [i["id"] for i in p3["items"]] == newest_first[10:]   # la última página trae las 2 más antiguas


def test_pagina_fuera_de_rango_devuelve_vacio(client):
    _crear(client, 3)

    res = client.get("/requests?page=5&size=5", headers=auth()).json()

    assert res["items"] == [] and res["total"] == 3


def test_listado_solo_muestra_solicitudes_propias(client):
    _crear(client, 2, user_id=1)
    _crear(client, 3, user_id=2)

    assert client.get("/requests", headers=auth(user_id=1)).json()["total"] == 2
    assert client.get("/requests", headers=auth(user_id=2)).json()["total"] == 3


@pytest.mark.parametrize("query", ["page=0", "size=0", "size=101", "page=abc"])
def test_parametros_de_paginacion_invalidos(client, query):
    res = client.get(f"/requests?{query}", headers=auth())

    assert res.status_code == 422


def test_listado_incluye_datos_del_medicamento(client, no_pos_data):
    client.post("/requests", json=no_pos_data, headers=auth())

    item = client.get("/requests", headers=auth()).json()["items"][0]

    assert item["medication"] == {"id": NO_POS_ID, "name": "Adalimumab 40 mg", "is_pos": False}
