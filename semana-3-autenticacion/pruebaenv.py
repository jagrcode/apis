import os
from pathlib import Path
from dotenv import load_dotenv

print("Script en:", Path(__file__).parent)
print("Carpeta de trabajo:", os.getcwd())
print(".env encontrado en:", find_dotenv() or "NO ENCONTRADO")

ruta = Path(__file__).parent / ".env"
print("¿Existe junto al script?", ruta.exists())

valores = dotenv_values(ruta)
print("Variables que lee el archivo:", list(valores.keys()))