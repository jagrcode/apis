import os
import requests
from dotenv import load_dotenv


load_dotenv()  # Carga las variables de entorno desde el archivo .env
token = os.getenv("GITHUB_TOKEN")  # Obtiene el token de GitHub desde las variables de entorno

if not token:
    raise ValueError("No se encontró el token de GitHub. Asegúrate de tener un archivo .env con la variable GITHUB_TOKEN.")

headers = {
    "Authorization": f"Bearer {token}", 
    "Accept": "application/vnd.github+json",
}

# Sin token 
r1 = requests.get("https://api.github.com/rate_limit", timeout=10 )
print("Sin token:", r1.json()["rate"]["limit"], "peticiones/hora")

# con Token 

r2 = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
print("Con token:", r2.json()["rate"]["limit"], "peticiones/hora")

# Quién soy según la API
r3 = requests.get("https://api.github.com/user", headers=headers, timeout=10)
print("Estado:", r3.status_code)
print("Usuario:", r3.json().get("login"))


r = requests.get(
    "https://api.github.com/user",
    headers={"Authorization": "Bearer token_falso"},
    timeout=10,
)
print(r.status_code, r.json())




# Basic auth
r = requests.get("https://httpbin.org/basic-auth/jaime/clave123",
                 auth=("jaime", "clave123"), timeout=10)
print("Basic:", r.status_code, r.json())

# Credenciales incorrectas
r = requests.get("https://httpbin.org/basic-auth/jaime/clave123",
                 auth=("jaime", "mala"), timeout=10)
print("Basic mala:", r.status_code)

# Bearer
r = requests.get("https://httpbin.org/bearer",
                 headers={"Authorization": "Bearer abc123"}, timeout=10)
print("Bearer:", r.status_code, r.json())

# API key en un header personalizado
r = requests.get("https://httpbin.org/headers",
                 headers={"X-API-Key": "mi-clave-de-prueba"}, timeout=10)
print("API key:", r.json()["headers"]["X-Api-Key"])