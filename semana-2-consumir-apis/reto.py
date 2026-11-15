import pandas as pd

df = pd.read_csv("repos_tiangolo.csv", encoding="utf-8-sig")

print("Total de repositorios:", len(df))

print("\nLenguajes más usados:")
print(df["lenguaje"].value_counts().head(5))

print("\nTop 5 por estrellas:")
print(df.sort_values("estrellas", ascending=False)[["nombre", "estrellas"]].head(5))

print("\nPromedio de estrellas por lenguaje:")
print(df.groupby("lenguaje")["estrellas"].mean().round(1).sort_values(ascending=False).head(5))