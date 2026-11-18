import requests

URL = "https://webhook.site/888665e0-8bba-4786-8854-8f3d9600b9a5"

evento = {"evento": "tarea.creada", "id": 7, "titulo": "Aprender webhooks"}
r = requests.post(URL, json=evento, headers={"X-Origen": "mi-api"}, timeout=10)
print("Respuesta:", r.status_code)

r = requests.post(URL, json=evento, headers={"X-Origen": "mi-api"}, timeout=10)
print("Respuesta:", r.status_code)
print("Cuerpo de la respuesta:", r.text[:200])