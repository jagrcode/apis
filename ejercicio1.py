import requests
import json

url = "https://pokeapi.co/api/v2/pokemon/pikachu"


def buscar_pokemon(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError:
        print(f"'{nombre}' no existe (código {respuesta.status_code}).")
        return None
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)
        return None

    datos = respuesta.json()
    return {
        "nombre": datos["name"],
        "altura": datos["height"],
        "peso": datos["weight"],
    }


def guardar_json(datos, archivo="pokemon.json"):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
    print(f"Guardado en {archivo}")

     
nombre =  input("Ingrese el nombre del Pokémon: ")
resultado = buscar_pokemon(nombre)
if resultado:
    guardar_json(resultado)