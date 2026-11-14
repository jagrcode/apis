import requests

r = requests.post(
    "https://httpbin.org/anything",
    params={"filtro": "demo"},
    headers={"X-Mi-Header": "hola"},
    json={"nombre": "Jaime", "curso": "APIs"},
    timeout=10,
)

import json
print(json.dumps(r.json(), indent=2))


r2 = requests.get(
    "https://httpbin.org/anything",
    params={"filtro": "demo"},
    headers={"X-Mi-Header": "hola"},
    json={"nombre": "Jaime", "curso": "APIs"},
    timeout=10,
)
print(json.dumps(r2.json(), indent=2))