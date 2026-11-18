import requests

URL = "https://countries.trevorblades.com/graphql"


def graphql(consulta, variables=None):
    r = requests.post(
        URL,
        json={"query": consulta, "variables": variables or {}},
        timeout=10,
    )
    r.raise_for_status()
    cuerpo = r.json()
    if "errors" in cuerpo:
        raise RuntimeError(cuerpo["errors"])
    return cuerpo["data"]


# 1. Lista simple: solo pides los campos que necesitas
datos = graphql("{ countries { name code } }")
print("Países:", len(datos["countries"]))

# 2. Un país con datos anidados en UNA sola petición
consulta = """
query Pais($codigo: ID!) {
  country(code: $codigo) {
    name
    capital
    currency
    emoji
    continent { name }
    languages { code name }
  }
}
"""
pais = graphql(consulta, {"codigo": "CO"})["country"]
print(pais)

# 3. Filtro
sur = graphql('{ countries(filter: {continent: {eq: "SA"}}) { name capital } }')
for p in sur["countries"]:
    print(p["name"], "-", p["capital"])

# 4. Un error: campo que no existe
try:
    graphql("{ countries { nombre } }")
except (RuntimeError, requests.HTTPError) as e:
    print("Error de GraphQL:", type(e).__name__)