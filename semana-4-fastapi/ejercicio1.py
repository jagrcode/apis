from fastapi import FastAPI

app= FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "Hola mi primera API con FastAPI"}

@app.get("/saludo/{nombre}")    
def saludo(nombre: str,mayusculas: bool = False):
    texto = f"Hola {nombre}, bienvenido a FastAPI"
    return {"Saludo": texto.upper() if mayusculas else texto}