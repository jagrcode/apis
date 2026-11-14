import requests
url = "https://pokeapi.co/api/v2/pokemon/pikachu"
respuesta = requests.get(url, timeout=15)
print("Código de estado:", respuesta.status_code)
print("Content-Type:", respuesta.headers["Content-Type"])

datos = respuesta.json()
print (datos)
print("Nombre:", datos["name"])
print("Altura:", datos["height"])
print("Peso:", datos["weight"])
print("Tipos:", [t["type"]["name"] for t in datos["types"]])

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

for nombre in ["pikachu", "charmander", "noexiste"]:
    print(buscar_pokemon(nombre))