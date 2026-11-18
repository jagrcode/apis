import sqlite3
from contextlib import contextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from auth import comprobar, crear_token, hashear, verificar_token

descripcion = """
API de práctica para gestionar tareas.

## Autenticación
1. Envía usuario y contraseña a `POST /login`.
2. Usa el `access_token` recibido en el header `Authorization: Bearer <token>`.

## Roles
* **admin**: puede crear, modificar y eliminar tareas.
* **lector**: solo puede consultar

Las rutas de lectura son públicas.
"""

tags_metadata = [
    {"name": "auth", "description": "Obtención del token de acceso."},
    {"name": "tareas", "description": "Consulta y gestión de tareas."},
]

app = FastAPI(
    title="API de tareas",
    description=descripcion,
    version="1.0.0",
    contact={"name": "Jaime"},
    license_info={"name": "MIT"},
    openapi_tags=tags_metadata,
)

# ---------- Base de datos ----------
DB = "tareas.db"


@contextmanager
def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def iniciar_db():
    with db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS tareas (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   titulo TEXT NOT NULL,
                   hecha INTEGER NOT NULL DEFAULT 0
               )"""
        )


iniciar_db()

# ---------- Modelos ----------


class TareaCrear(BaseModel):
    titulo: str = Field(
        ..., min_length=3, max_length=80,
        description="Texto corto de la tarea",
        examples=["Estudiar OpenAPI"],
    )
    hecha: bool = Field(False, description="Si la tarea ya se completó")

class Tarea(TareaCrear):
    id: int

class Error(BaseModel):
    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str

class Resumen(BaseModel):
    total: int
    hechas: int
    pendientes: int

R401 = {401: {"model": Error, "description": "Token ausente, inválido o vencido"}}
R403 = {403: {"model": Error, "description": "El rol no tiene permiso"}}
R404 = {404: {"model": Error, "description": "La tarea no existe",
              "content": {"application/json": {"example": {"detail": "Tarea no encontrada"}}}}}     


def a_tarea(fila) -> Tarea:
    return Tarea(id=fila["id"], titulo=fila["titulo"], hecha=bool(fila["hecha"]))


# ---------- Autenticación ----------
# Usuario de práctica. En una API real los usuarios viven en la base de datos.
USUARIOS = {"jaime": {"hash": hashear("demo1234"), "rol": "admin"},
              "lector": {"hash": hashear("demo1234"), "rol": "lector"}}

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login", response_model=Token, tags=["auth"],
          summary="Iniciar sesión",
          responses={401: {"model": Error, "description": "Credenciales incorrectas"}})

def login(form: OAuth2PasswordRequestForm = Depends()):
    """Devuelve un token de acceso que vence a los 30 minutos."""

    usuario = USUARIOS.get(form.username)
    if not usuario or not comprobar(form.password, usuario["hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = crear_token(form.username, usuario["rol"])
    return {"access_token": token, "token_type": "bearer"}


def usuario_actual(token: str = Depends(oauth2)):
    datos = verificar_token(token)
    if not datos:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o vencido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return datos

def requiere_admin(usuario: dict = Depends(usuario_actual)):
    if usuario["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol admin")
    return usuario

# ---------- Rutas CRUD ----------


@app.get("/tareas", response_model=list[Tarea], tags=["tareas"],
         summary="Listar tareas")
def listar(
    limit: int = Query(10, ge=1, le=100, description="Máximo de tareas a devolver"),
    offset: int = Query(0, ge=0, description="Cuántas tareas saltar"),
    hecha: bool | None = Query(None, description="Filtrar por estado"),
):
    sql = "SELECT * FROM tareas"
    valores = []

    if hecha is not None:
        sql += " WHERE hecha = ?"
        valores.append(int(hecha))

    sql += " ORDER BY id LIMIT ? OFFSET ?"
    valores += [limit, offset]

    with db() as con:
        filas = con.execute(sql, valores).fetchall()
    return [a_tarea(f) for f in filas]


@app.get("/tareas/resumen", response_model=Resumen, tags=["tareas"],
         summary="Resumen de tareas")
def resumen():
    """Cuenta las tareas totales, hechas y pendientes."""
    with db() as con:
        fila = con.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(hecha), 0) AS hechas FROM tareas"
        ).fetchone()
    return Resumen(
        total=fila["total"],
        hechas=fila["hechas"],
        pendientes=fila["total"] - fila["hechas"],
    )

@app.get("/tareas/{tarea_id}", response_model=Tarea, tags=["tareas"],
         summary="Obtener una tarea por ID", responses={**R404})
def obtener(tarea_id: int):
    with db() as con:
        fila = con.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return a_tarea(fila)



@app.post("/tareas", response_model=Tarea, status_code=201, tags=["tareas"],
          summary="Crear una nueva tarea", responses={**R401, **R403})
def crear(datos: TareaCrear, usuario: dict = Depends(requiere_admin)):
    with db() as con:
        cur = con.execute(
            "INSERT INTO tareas (titulo, hecha) VALUES (?, ?)",
            (datos.titulo, int(datos.hecha)),
        )
        nuevo_id = cur.lastrowid
    return Tarea(id=nuevo_id, **datos.model_dump())


@app.put("/tareas/{tarea_id}", response_model=Tarea, tags=["tareas"],
         summary="Reemplazar una tarea", responses={**R401, **R404, **R403})
def reemplazar(tarea_id: int, datos: TareaCrear, usuario: dict = Depends(requiere_admin)):
    with db() as con:
        cur = con.execute(
            "UPDATE tareas SET titulo = ?, hecha = ? WHERE id = ?",
            (datos.titulo, int(datos.hecha), tarea_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return Tarea(id=tarea_id, **datos.model_dump())


@app.put("/tareas/{tarea_id}/hecha", response_model=Tarea, tags=["tareas"],
         summary="Marcar tarea como hecha o pendiente", responses={**R401, **R404, **R403})
def marcar_como_hecha(tarea_id: int, 
                      hecha: bool, 
                      usuario: dict = Depends(requiere_admin),
                      ):  
    """Cambia el estado de una tarea. **Solo el rol `admin`.**

    Es idempotente: repetir la misma petición deja el mismo resultado.
    """
    with db() as con:
        cur = con.execute(
            "UPDATE tareas SET hecha = ? WHERE id = ?",
            (int(hecha), tarea_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        fila = con.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    return a_tarea(fila)

@app.delete("/tareas/{tarea_id}", status_code=204, tags=["tareas"],
            summary="Eliminar una tarea",
            responses={**R401, **R403, **R404})
def eliminar(tarea_id: int, usuario: dict = Depends(requiere_admin)):
    """Elimina una tarea. **Solo el rol `admin`.**"""

    with db() as con:
        
            cur = con.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Tarea no encontrada")