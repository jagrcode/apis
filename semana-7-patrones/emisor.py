import hashlib
import hmac
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
SECRETO = os.getenv("WEBHOOK_SECRET")

cuerpo = json.dumps({"evento": "tarea.creada", "id": 1, "titulo": "Probar webhook"}).encode()
firma = hmac.new(SECRETO.encode(), cuerpo, hashlib.sha256).hexdigest()

# Con firma correcta
r = requests.post(
    "http://127.0.0.1:8000/webhook",
    data=cuerpo,
    headers={"Content-Type": "application/json", "X-Firma": firma},
    timeout=10,
)
print("Firma correcta:", r.status_code)

# Con firma falsa
r = requests.post(
    "http://127.0.0.1:8000/webhook",
    data=cuerpo,
    headers={"Content-Type": "application/json", "X-Firma": "falsa"},
    timeout=10,
)
print("Firma falsa:", r.status_code)