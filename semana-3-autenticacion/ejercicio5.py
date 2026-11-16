import datetime as dt
import jwt
import base64
import json
import os 
from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")
CLAVE = os.getenv("JWT_SECRET")
if not CLAVE:
    sys.exit("Falta JWT_SECRET en el archivo .env")

# 1. Crear un token que vence en 30 minutos
ahora = dt.datetime.now(dt.timezone.utc)
payload = {
    "sub": "jaime",
    "rol": "estudiante",
    "iat": ahora,
    "iss": "mi-api",
    "exp": ahora + dt.timedelta(minutes=30),
}


token = jwt.encode(payload, CLAVE, algorithm="HS256")
print("Token:", token)

datos = jwt.decode(token, CLAVE, algorithms=["HS256"], issuer="mi-api")

try:
    jwt.decode(token, CLAVE, algorithms=["HS256"], issuer="otra-api")
except jwt.InvalidIssuerError:
    print("El emisor no coincide.") 

    


# 1. Crear un token que vence en 30 minutos
ahora = dt.datetime.now(dt.timezone.utc)
payload = {
    "sub": "jaime",
    "rol": "estudiante",
    "iat": ahora,
    "exp": ahora + dt.timedelta(minutes=30),
}
token = jwt.encode(payload, CLAVE, algorithm="HS256")
print("Token:", token)


# 2. Leer el payload SIN verificar la firma
print("Payload visible:", jwt.decode(token, options={"verify_signature": False}))


# 3. Verificar con la clave correcta
datos = jwt.decode(token, CLAVE, algorithms=["HS256"])
print("Verificado:", datos["sub"], datos["rol"])


# 4. Clave incorrecta
try:
    jwt.decode(token, "otra-clave", algorithms=["HS256"])
except jwt.InvalidSignatureError:
    print("Firma inválida: la clave no coincide.")


# 5. Token vencido
vencido = jwt.encode(
    {"sub": "jaime", "exp": ahora - dt.timedelta(seconds=1)},
    CLAVE,
    algorithm="HS256",
)

try:
    jwt.decode(vencido, CLAVE, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("El token ya venció.")


partes = token.split(".")
payload_falso = base64.urlsafe_b64encode(
    json.dumps({"sub": "jaime", "rol": "admin"}).encode()
).rstrip(b"=").decode()

token_falso = f"{partes[0]}.{payload_falso}.{partes[2]}"

try:
    jwt.decode(token_falso, CLAVE, algorithms=["HS256"])
except jwt.InvalidSignatureError:
    print("Intento de alteración detectado.")