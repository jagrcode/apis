import hashlib
import hmac
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request

load_dotenv(Path(__file__).parent / ".env")
SECRETO = os.getenv("WEBHOOK_SECRET")
if not SECRETO:
    raise RuntimeError("Falta WEBHOOK_SECRET en el archivo .env")

app = FastAPI(title="Receptor de webhooks")
eventos: list[dict] = []


def firmar(cuerpo: bytes) -> str:
    return hmac.new(SECRETO.encode(), cuerpo, hashlib.sha256).hexdigest()


@app.post("/webhook")
async def recibir(request: Request, x_firma: str = Header(default="")):
    cuerpo = await request.body()          # los bytes EXACTOS que llegaron
    if not hmac.compare_digest(firmar(cuerpo), x_firma):
        raise HTTPException(status_code=401, detail="Firma inválida")
    eventos.append(json.loads(cuerpo))
    return {"recibido": True}


@app.get("/eventos")
def listar():
    return eventos