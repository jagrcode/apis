import sqlite3
from contextlib import contextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from auth import comprobar, crear_token, hashear, verificar_token

app = FastAPI(title="API de tareas", version="1.0.0")

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
    titulo: str = Field(..., min_length=3, max_length=80)
    hecha: bool = False


class Tarea(TareaCrear):
    id: int


def a_tarea(fila) -> Tarea:
    return Tarea(id=fila["id"], titulo=fila["titulo"], hecha=bool(fila["hecha"]))


# ---------- Autenticación ----------
# Usuario de práctica. En una API real los usuarios viven en la base de datos.
USUARIOS = {"jaime": {"hash": hashear("demo1234"), "rol": "admin"},
              "lector": {"hash": hashear("demo1234"), "rol": "lector"}}

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login", tags=["auth"])
def login(form: OAuth2PasswordRequestForm = Depends()):
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


# ---------- Rutas CRUD ----------


@app.get("/tareas", response_model=list[Tarea], tags=["tareas"])
def listar():
    limit = 3
    with db() as con:
        filas = con.execute("SELECT * FROM tareas ORDER BY id LIMIT ?", (limit,)).fetchall()
    return [a_tarea(f) for f in filas]


@app.get("/tareas/{tarea_id}", response_model=Tarea, tags=["tareas"])
def obtener(tarea_id: int):
    with db() as con:
        fila = con.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return a_tarea(fila)


@app.get("/tareas/{hecha}", response_model=Tarea, tags=["tareas"])
def obtener2(hecha: bool):
    with db() as con:
        filas = con.execute("SELECT * FROM tareas WHERE hecha = ?", (int(hecha),)).fetchall()
    return [a_tarea(f) for f in filas]


@app.post("/tareas", response_model=Tarea, status_code=201, tags=["tareas"])
def crear(datos: TareaCrear, usuario: dict = Depends(usuario_actual)):
    with db() as con:
        cur = con.execute(
            "INSERT INTO tareas (titulo, hecha) VALUES (?, ?)",
            (datos.titulo, int(datos.hecha)),
        )
        nuevo_id = cur.lastrowid
    return Tarea(id=nuevo_id, **datos.model_dump())


@app.put("/tareas/{tarea_id}", response_model=Tarea, tags=["tareas"])
def reemplazar(tarea_id: int, datos: TareaCrear, usuario: dict = Depends(usuario_actual)):
    with db() as con:
        cur = con.execute(
            "UPDATE tareas SET titulo = ?, hecha = ? WHERE id = ?",
            (datos.titulo, int(datos.hecha), tarea_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return Tarea(id=tarea_id, **datos.model_dump())


@app.delete("/tareas/{tarea_id}", status_code=204, tags=["tareas"])
def eliminar(tarea_id: int, usuario: dict = Depends(usuario_actual)):
    with db() as con:
        if usuario["rol"] != "admin":
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar tareas")
        else:
            cur = con.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Tarea no encontrada")