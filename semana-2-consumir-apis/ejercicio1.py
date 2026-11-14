import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def crear_sesion():
    """Sesión que reintenta solo ante errores transitorios."""
    sesion = requests.Session()

    reintentos = Retry(
        total=3,
        backoff_factor=1,                        # espera 1s, 2s, 4s...
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )
    adaptador = HTTPAdapter(max_retries=reintentos)
    sesion.mount("https://", adaptador)
    sesion.mount("http://", adaptador)

    sesion.headers.update({"User-Agent": "mi-curso-apis/1.0"})
    return sesion


def obtener_todos(sesion, url, params=None, maximo=None, pausa=0.5):
    resultados = []
    peticiones = 0

    while url:
        try:
            r = sesion.get(url, params=params, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RetryError:
            print("Se agotaron los reintentos. Devuelvo lo descargado hasta ahora.")
            break
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Devuelvo lo descargado hasta ahora.")
            break

        peticiones += 1
        datos = r.json()
        resultados.extend(datos["results"])
        print(f"Petición {peticiones}: {len(resultados)} de {datos['count']}")

        if maximo and len(resultados) >= maximo:
            resultados = resultados[:maximo]
            break

        url = datos["next"]    # None cuando no hay más páginas
        params = None          # la URL "next" ya trae limit y offset
        time.sleep(pausa)      # cortesía con el servidor

    print(f"Total de peticiones: {peticiones}")
    return resultados


if __name__ == "__main__":
    sesion = crear_sesion()
    pokemones = obtener_todos(
        sesion,
        "https://pokeapi.co/api/v2/pokemon",
        params={"limit": 5},
        maximo=300,
    )
    print("Total descargado:", len(pokemones))
    print("Primeros 5:", [p["name"] for p in pokemones[:5]])