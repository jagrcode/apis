import pytest


def crear_tarea(cliente, headers, titulo="Tarea de prueba"):
    r = cliente.post("/tareas", json={"titulo": titulo}, headers=headers)
    assert r.status_code == 201
    return r.json()


# ---------- Lectura ----------

def test_listar_vacio(cliente):
    r = cliente.get("/tareas")
    assert r.status_code == 200
    assert r.json() == []


def test_obtener_inexistente_da_404(cliente):
    r = cliente.get("/tareas/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Tarea no encontrada"}


# ---------- Autenticación ----------

def test_login_correcto_devuelve_token(cliente):
    r = cliente.post("/login", data={"username": "jaime", "password": "demo1234"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_con_clave_incorrecta_da_401(cliente):
    r = cliente.post("/login", data={"username": "jaime", "password": "mala"})
    assert r.status_code == 401


def test_crear_sin_token_da_401(cliente):
    r = cliente.post("/tareas", json={"titulo": "Sin permiso"})
    assert r.status_code == 401


def test_crear_con_token_falso_da_401(cliente):
    r = cliente.post(
        "/tareas",
        json={"titulo": "Token falso"},
        headers={"Authorization": "Bearer token_falso"},
    )
    assert r.status_code == 401


# ---------- Roles ----------

def test_lector_no_puede_crear(cliente, headers_lector):
    r = cliente.post("/tareas", json={"titulo": "Prueba"}, headers=headers_lector)
    assert r.status_code == 403


def test_lector_no_puede_eliminar(cliente, headers_admin, headers_lector):
    tarea = crear_tarea(cliente, headers_admin)
    r = cliente.delete(f"/tareas/{tarea['id']}", headers=headers_lector)
    assert r.status_code == 403
    # La tarea sigue existiendo
    assert cliente.get(f"/tareas/{tarea['id']}").status_code == 200


# ---------- Escritura ----------

def test_admin_crea_y_consulta(cliente, headers_admin):
    tarea = crear_tarea(cliente, headers_admin, "Estudiar pytest")
    assert tarea["titulo"] == "Estudiar pytest"
    assert tarea["hecha"] is False

    r = cliente.get(f"/tareas/{tarea['id']}")
    assert r.status_code == 200
    assert r.json() == tarea


@pytest.mark.parametrize("titulo", ["ab", "x" * 81, ""])
def test_titulo_invalido_da_422(cliente, headers_admin, titulo):
    r = cliente.post("/tareas", json={"titulo": titulo}, headers=headers_admin)
    assert r.status_code == 422


def test_marcar_hecha_conserva_el_titulo(cliente, headers_admin):
    # Prueba de regresión: antes esta ruta devolvía 500 por un título vacío
    tarea = crear_tarea(cliente, headers_admin, "Terminar semana 6")
    r = cliente.put(
        f"/tareas/{tarea['id']}/hecha", params={"hecha": True}, headers=headers_admin
    )
    assert r.status_code == 200
    assert r.json()["titulo"] == "Terminar semana 6"
    assert r.json()["hecha"] is True


def test_marcar_hecha_en_tarea_inexistente_da_404(cliente, headers_admin):
    r = cliente.put("/tareas/999/hecha", params={"hecha": True}, headers=headers_admin)
    assert r.status_code == 404


def test_admin_elimina(cliente, headers_admin):
    tarea = crear_tarea(cliente, headers_admin)
    r = cliente.delete(f"/tareas/{tarea['id']}", headers=headers_admin)
    assert r.status_code == 204
    assert cliente.get(f"/tareas/{tarea['id']}").status_code == 404


def test_eliminar_inexistente_da_404(cliente, headers_admin):
    r = cliente.delete("/tareas/999", headers=headers_admin)
    assert r.status_code == 404


# ---------- Paginación, filtro y resumen ----------

def test_paginacion(cliente, headers_admin):
    for i in range(1, 6):
        crear_tarea(cliente, headers_admin, f"Tarea {i}")
    r = cliente.get("/tareas", params={"limit": 2, "offset": 2})
    assert [t["titulo"] for t in r.json()] == ["Tarea 3", "Tarea 4"]


@pytest.mark.parametrize("limit", [0, 101])
def test_limit_fuera_de_rango_da_422(cliente, limit):
    assert cliente.get("/tareas", params={"limit": limit}).status_code == 422


def test_filtro_por_hecha(cliente, headers_admin):
    a = crear_tarea(cliente, headers_admin, "Tarea A")
    crear_tarea(cliente, headers_admin, "Tarea B")
    cliente.put(f"/tareas/{a['id']}/hecha", params={"hecha": True}, headers=headers_admin)

    r = cliente.get("/tareas", params={"hecha": True})
    assert [t["id"] for t in r.json()] == [a["id"]]


def test_resumen(cliente, headers_admin):
    ids = [crear_tarea(cliente, headers_admin, f"Tarea {n}")["id"] for n in (1, 2, 3)]
    cliente.put(f"/tareas/{ids[0]}/hecha", params={"hecha": True}, headers=headers_admin)

    r = cliente.get("/tareas/resumen")
    assert r.status_code == 200
    assert r.json() == {"total": 3, "hechas": 1, "pendientes": 2}


# ---------- Reemplazar (PUT /tareas/{id}) ----------

def test_admin_reemplaza(cliente, headers_admin):
    tarea = crear_tarea(cliente, headers_admin, "Titulo viejo")
    r = cliente.put(
        f"/tareas/{tarea['id']}",
        json={"titulo": "Titulo nuevo", "hecha": True},
        headers=headers_admin,
    )
    assert r.status_code == 200
    assert r.json() == {"id": tarea["id"], "titulo": "Titulo nuevo", "hecha": True}

    # Verifica que el cambio quedó guardado, no solo que la respuesta lo diga
    guardada = cliente.get(f"/tareas/{tarea['id']}").json()
    assert guardada["titulo"] == "Titulo nuevo"
    assert guardada["hecha"] is True


def test_lector_no_puede_reemplazar(cliente, headers_admin, headers_lector):
    tarea = crear_tarea(cliente, headers_admin, "Titulo original")
    r = cliente.put(
        f"/tareas/{tarea['id']}",
        json={"titulo": "Intento del lector"},
        headers=headers_lector,
    )
    assert r.status_code == 403
    # La tarea no cambió
    assert cliente.get(f"/tareas/{tarea['id']}").json()["titulo"] == "Titulo original"


def test_reemplazar_inexistente_da_404(cliente, headers_admin):
    r = cliente.put("/tareas/999", json={"titulo": "No existe"}, headers=headers_admin)
    assert r.status_code == 404


def test_reemplazar_sin_token_da_401(cliente):
    r = cliente.put("/tareas/1", json={"titulo": "Sin token"})
    assert r.status_code == 401


# ---------- Paginación completa ----------

def test_paginacion_completa_sin_repetir(cliente, headers_admin):
    creadas = [
        crear_tarea(cliente, headers_admin, f"Tarea {i}")["id"] for i in range(1, 6)
    ]

    recibidas = []
    for offset in (0, 2, 4):
        r = cliente.get("/tareas", params={"limit": 2, "offset": offset})
        assert r.status_code == 200
        recibidas += [t["id"] for t in r.json()]

    # Todas, en orden y sin repetir ni faltar ninguna
    assert recibidas == creadas


@pytest.mark.parametrize(
    "offset, esperadas",
    [(0, 2), (2, 2), (4, 1), (6, 0)],
    ids=["primera", "segunda", "ultima_incompleta", "mas_alla_del_final"],
)
def test_tamano_de_cada_pagina(cliente, headers_admin, offset, esperadas):
    for i in range(1, 6):
        crear_tarea(cliente, headers_admin, f"Tarea {i}")
    r = cliente.get("/tareas", params={"limit": 2, "offset": offset})
    assert r.status_code == 200
    assert len(r.json()) == esperadas


# ---------- Contrato OpenAPI ----------

def test_contrato_publica_la_informacion_basica(cliente):
    r = cliente.get("/openapi.json")
    assert r.status_code == 200

    contrato = r.json()
    assert contrato["info"]["title"] == "API de tareas"
    assert contrato["info"]["version"] == "1.0.0"

    rutas = contrato["paths"]
    for ruta in ("/login", "/tareas", "/tareas/resumen",
                 "/tareas/{tarea_id}", "/tareas/{tarea_id}/hecha"):
        assert ruta in rutas, f"Falta {ruta} en el contrato"


def test_contrato_documenta_los_errores_correctos(cliente):
    rutas = cliente.get("/openapi.json").json()["paths"]

    # Eliminar: éxito sin contenido, y los tres errores
    eliminar = rutas["/tareas/{tarea_id}"]["delete"]["responses"]
    assert {"204", "401", "403", "404"} <= set(eliminar)

    # Las rutas de lectura son públicas: no deben prometer un 401
    assert "401" not in rutas["/tareas"]["get"]["responses"]
    assert "401" not in rutas["/tareas/{tarea_id}"]["get"]["responses"]