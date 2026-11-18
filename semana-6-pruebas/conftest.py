import os
import tempfile

# Estas variables deben fijarse ANTES de importar main y auth.
# Así las pruebas nunca usan tu clave real ni tu base real.
os.environ["JWT_SECRET"] = "clave-de-pruebas-" + "0123456789abcdef" * 4
os.environ["TAREAS_DB"] = os.path.join(tempfile.mkdtemp(), "importacion.db")

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    """Cliente de la API con una base de datos nueva y vacía en cada prueba."""
    monkeypatch.setattr(main, "DB", str(tmp_path / "prueba.db"))
    main.iniciar_db()
    return TestClient(main.app)


def _headers(cliente, usuario):
    r = cliente.post("/login", data={"username": usuario, "password": "demo1234"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def headers_admin(cliente):
    return _headers(cliente, "jaime")


@pytest.fixture
def headers_lector(cliente):
    return _headers(cliente, "lector")