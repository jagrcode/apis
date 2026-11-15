import csv
import time
import requests
import os
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry




load_dotenv()  # Carga las variables de entorno desde el archivo .env
token = os.getenv("GITHUB_TOKEN")  # Obtiene el token de GitHub desde las variables de entorno


def crear_sesion():
    """Sesión que reintenta solo ante errores transitorios."""
    sesion = requests.Session()
    sesion.headers.update({"Authorization": f"Bearer {token}"})
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



def mostrar_limite(r):
    restantes = r.headers.get("X-RateLimit-Remaining")
    total = r.headers.get("X-RateLimit-Limit")
    print(f"   Límite: {restantes}/{total} peticiones restantes")


def repos_de_usuario(sesion, usuario, por_pagina=100):
    url = f"https://api.github.com/users/{usuario}/repos"
    params = {"per_page": por_pagina, "sort": "updated"}
    repos = []
    pagina = 0

    sesion.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })

    while url:
        r = sesion.get(url, params=params, timeout=10)

        if r.status_code == 404:
            print(f"El usuario '{usuario}' no existe.")
            return []

        if r.status_code in (403, 429) and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers["X-RateLimit-Reset"])
            espera = max(0, reset - int(time.time()))
            print(f"Límite agotado. Se reinicia en {espera // 60} min.")
            break

        r.raise_for_status()
        pagina += 1
        repos.extend(r.json())
        print(f"Página {pagina}: {len(repos)} repositorios")
        mostrar_limite(r)

        # requests interpreta el header Link y lo expone en r.links
        url = r.links.get("next", {}).get("url")
        params = None     # la URL "next" ya trae los parámetros
        time.sleep(0.5)

    return repos


def guardar_csv(filas, archivo, columnas):
    with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"Guardadas {len(filas)} filas en {archivo}")


if __name__ == "__main__":
    usuario = input("Usuario de GitHub: ").strip()
    sesion = crear_sesion()
    repos = repos_de_usuario(sesion, usuario)

    filas = [
        {
            "nombre": r["name"],
            "lenguaje": r["language"] or "N/A",
            "estrellas": r["stargazers_count"],
            "forks": r["forks_count"],
            "actualizado": r["updated_at"][:10],
            "url": r["html_url"],
        }
        for r in repos
    ]

    if filas:
        guardar_csv(filas, f"repos_{usuario}.csv",
                    ["nombre", "lenguaje", "estrellas", "forks", "actualizado", "url"])