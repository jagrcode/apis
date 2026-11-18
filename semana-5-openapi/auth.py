import datetime as dt
import hashlib
import hmac
import os
from pathlib import Path

import jwt
from dotenv import load_dotenv


load_dotenv(Path(__file__).parent / ".env")
CLAVE = os.getenv("JWT_SECRET")

if not CLAVE:
    raise RuntimeError("Falta JWT_SECRET en el archivo .env")

EMISOR = "mi-api"


def hashear(clave: str) -> str:
    """Guarda la contraseña como hash con sal, nunca en texto plano."""
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, 200_000)
    return f"{sal.hex()}:{h.hex()}"


def comprobar(clave: str, guardado: str) -> bool:
    sal_hex, h_hex = guardado.split(":")
    nuevo = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal_hex), 200_000)
    return hmac.compare_digest(nuevo.hex(), h_hex)


def crear_token(usuario: str, rol: str, minutos: int = 30) -> str:
    ahora = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": usuario,
        "rol": rol,
        "iss": EMISOR,
        "iat": ahora,
        "exp": ahora + dt.timedelta(minutes=minutos),
    }
    return jwt.encode(payload, CLAVE, algorithm="HS256")


def verificar_token(token: str):
    """Devuelve los datos del token, o None si no es válido."""
    try:
        return jwt.decode(token, CLAVE, algorithms=["HS256"], issuer=EMISOR)
    except jwt.InvalidTokenError:
        return None