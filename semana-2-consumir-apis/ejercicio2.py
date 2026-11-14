import time
import requests
import ejercicio1
CODIGOS_REINTENTABLES = {429, 500, 502, 503, 504}

def get_con_reintentos(url, intentos=4, espera_base=1, **kwargs):
    for intento in range(1, intentos + 1):
        try:
            r = requests.get(url, timeout=10, **kwargs)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            print(f"Intento {intento}: error de conexión ({e.__class__.__name__})")
        else:
            if r.status_code not in CODIGOS_REINTENTABLES:
                return r   # éxito, o un error que no vale la pena reintentar (404, 401...)
            print(f"Intento {intento}: código {r.status_code}")

            # Si el servidor indica cuánto esperar, respétalo
            retry_after = r.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))
                continue

        if intento < intentos:
            espera = espera_base * (2 ** (intento - 1))   # 1, 2, 4, 8...
            print(f"   Esperando {espera}s antes de reintentar...")
            time.sleep(espera)

    raise RuntimeError(f"Falló después de {intentos} intentos: {url}")

# Prueba 1: siempre responde 503, debe agotar los intentos
try:
    get_con_reintentos("https://httpbin.org/status/503", intentos=3)
except RuntimeError as e:
    print("Error final:", e)

# Prueba 2: responde 200 a la primera
r = get_con_reintentos("https://httpbin.org/status/200")
print("Éxito:", r.status_code)

# Prueba 3: 404 no se reintenta (es culpa tuya, no del servidor)
r = get_con_reintentos("https://httpbin.org/status/404")
print("404 devuelto sin reintentos:", r.status_code)


from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sesion = requests.Session()

reintentos = Retry(
    total=3,
    backoff_factor=1,                       # espera 1s, 2s, 4s...
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],                # solo reintenta métodos seguros
    respect_retry_after_header=True,
)

adaptador = HTTPAdapter(max_retries=reintentos)
sesion.mount("https://", adaptador)
sesion.mount("http://", adaptador)

sesion.headers.update({"User-Agent": "mi-curso-apis/1.0"})

try:
    r = sesion.get("https://httpbin.org/status/503", timeout=10)
except requests.exceptions.RetryError as e:
    print("Reintentos agotados:", e)

try:
    r = sesion.get("https://httpbin.org/status/503", timeout=10)
except requests.exceptions.RetryError as e:
    print("Reintentos agotados:", e)