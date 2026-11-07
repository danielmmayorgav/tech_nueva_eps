"""Tests del manejo centralizado de errores (errors.py)."""
import pytest
from sqlalchemy.exc import DataError, IntegrityError, OperationalError

from main import app


def _raiser(exc):
    def endpoint():
        raise exc
    return endpoint


@pytest.fixture()
def failing_routes():
    """Agrega rutas temporales que fallan a propósito y las quita al terminar el test."""
    routes = {
        "/_test/integrity": IntegrityError("INSERT", {}, Exception("duplicate key")),
        "/_test/data": DataError("INSERT", {}, Exception("Out of range value for column 'phone'")),
        "/_test/operational": OperationalError("SELECT", {}, Exception("Can't connect to MySQL")),
        "/_test/bug": ZeroDivisionError("bug inesperado"),
    }
    before = list(app.router.routes)
    for path, exc in routes.items():
        app.add_api_route(path, _raiser(exc))
    yield
    app.router.routes[:] = before


@pytest.mark.parametrize("path, status", [
    ("/_test/integrity", 409),
    ("/_test/data", 422),
    ("/_test/operational", 503),
    ("/_test/bug", 500),
])
def test_errores_se_traducen_a_json(client, failing_routes, path, status):
    res = client.get(path)

    assert res.status_code == status
    assert "detail" in res.json()
    # Nunca se filtran detalles internos (SQL, nombres de columnas, trazas) al cliente
    assert "phone" not in res.text and "MySQL" not in res.text and "Traceback" not in res.text


def test_error_500_lleva_cabeceras_cors(client, failing_routes):
    res = client.get("/_test/bug", headers={"Origin": "http://localhost:5173"})

    assert res.status_code == 500
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_errores_quedan_registrados_en_log(client, failing_routes, caplog):
    with caplog.at_level("WARNING", logger="app"):
        client.get("/_test/data")
        client.get("/_test/bug")

    assert "Out of range value for column 'phone'" in caplog.text  # el detalle sí va al log
    assert "Error no controlado en GET /_test/bug" in caplog.text
