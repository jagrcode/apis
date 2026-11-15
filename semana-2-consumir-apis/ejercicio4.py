import csv
from ejercicio3 import crear_sesion, obtener_todos


def extraer_id(url):
    # "https://pokeapi.co/api/v2/pokemon/25/" -> 25
    return int(url.rstrip("/").split("/")[-1])


def guardar_csv(filas, archivo, columnas):
    with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"Guardadas {len(filas)} filas en {archivo}")


sesion = crear_sesion()
pokemones = obtener_todos(
    sesion,
    "https://pokeapi.co/api/v2/pokemon",
    params={"limit": 100},
   # maximo=300,
)

filas = [
    {"id": extraer_id(p["url"]), "nombre": p["name"], "url": p["url"]}
    for p in pokemones
]

guardar_csv(filas, "pokemones.csv", ["id", "nombre", "url"])

import time

def obtener_detalle(sesion, url):
    r = sesion.get(url, timeout=10)
    r.raise_for_status()
    d = r.json()
    return {
        "id": d["id"],
        "nombre": d["name"],
        "altura": d["height"],
        "peso": d["weight"],
        "tipos": ", ".join(t["type"]["name"] for t in d["types"]),
    }


detalles = []
for p in pokemones[:20]:
    try:
        detalles.append(obtener_detalle(sesion, p["url"]))
    except Exception as e:
        print(f"Falló {p['name']}: {e}")
    time.sleep(0.3)

guardar_csv(detalles, "pokemones_detalle.csv",
            ["id", "nombre", "altura", "peso", "tipos"])

def leer_csv(archivo="pokemones_detalle.csv"):
    with open(archivo, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        print("Columnas:", lector.fieldnames)
        filas = list(lector)          # lee todo una sola vez

    print("Primeras 5 filas:")
    for fila in filas[:5]:
        print(fila)
    return filas



def agregar_peso_kg(archivo="pokemones_detalle.csv"):
    with open(archivo, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        columnas = lector.fieldnames + ["peso_kg"]
        filas = []
        for fila in lector:
            fila["peso_kg"] = round(int(fila["peso"]) / 10, 1)
            filas.append(fila)

    guardar_csv(filas, "pokemones_detalle_kg.csv", columnas)
    return filas

    
import pandas as pd

df = pd.DataFrame(detalles)
print(df.head())
print(df.describe())              # estadísticas de altura y peso
df.to_csv("pokemones_pandas.csv", index=False, encoding="utf-8-sig")
lectura = leer_csv()
conpeso= agregar_peso_kg()
print("Primeras 5 filas con peso en kg:")
for fila in conpeso[:5]:
    print(fila) 