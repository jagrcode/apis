import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

URL_GITHUB = "https://api.github.com/graphql"
token = os.getenv("GITHUB_TOKEN")
if not token:
    sys.exit("Falta GITHUB_TOKEN en el archivo .env")


def graphql(url, consulta, variables=None, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.post(
        url,
        json={"query": consulta, "variables": variables or {}},
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
    cuerpo = r.json()
    if "errors" in cuerpo:
        raise RuntimeError(cuerpo["errors"])
    return cuerpo["data"]


CONSULTA = """
query($n: Int!) {
  viewer {
    login
    repositories(first: $n, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes { name isPrivate stargazerCount }
    }
  }
  rateLimit { cost remaining resetAt }
}
"""

datos = graphql(URL_GITHUB, CONSULTA, {"n": 5}, token=token)
usuario = datos["viewer"]

print("Usuario:", usuario["login"])
print("Total de repositorios:", usuario["repositories"]["totalCount"])
for repo in usuario["repositories"]["nodes"]:
    print("-", repo["name"], "(privado)" if repo["isPrivate"] else "")

limite = datos["rateLimit"]
print("Costo de la consulta:", limite["cost"], "| puntos restantes:", limite["remaining"])