import requests

BASE = "http://127.0.0.1:8000"

# 1. Login: el formulario se envía con data=, no json=
r = requests.post(f"{BASE}/login", data={"username": "jaime", "password": "demo1234"}, timeout=10)
r.raise_for_status()
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Crear
r = requests.post(f"{BASE}/tareas", json={"titulo": "Aprender FastAPI"}, headers=headers, timeout=10)
print("Crear:", r.status_code, r.json())

# 3. Listar
print("Listar:", requests.get(f"{BASE}/tareas", timeout=10).json())

# 4. Sin token
r = requests.post(f"{BASE}/tareas", json={"titulo": "Sin permiso"}, timeout=10)
print("Sin token:", r.status_code)