import time

import requests

def obtener_todos(url, params=None, maximo=None):
    resultados = []
    while url:
        time.sleep(0.5)
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        datos = r.json()

        resultados.extend(datos["results"])
        print(f"Descargados: {len(resultados)} de {datos['count']}")

        if maximo and len(resultados) >= maximo:
            break

        url = datos["next"]   # None cuando no hay más páginas
        params = None         # la URL "next" ya trae los parámetros
    return resultados

pokemones = obtener_todos(
    "https://pokeapi.co/api/v2/pokemon",
    params={"limit": 100},
    maximo=500,
)

print("Total descargado:", len(pokemones))
print("Primeros 5:", [p["name"] for p in pokemones[:5]])