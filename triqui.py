import tkinter as tk

ventana = tk.Tk()

ventana.title("Tres en Raya")
ventana.geometry("400x400")

# Crear las 9 casillas
for fila in range(3):
    for columna in range(3):

        boton = tk.Button(
            ventana,
            text="",
            font=("Arial", 30),
            width=5,
            height=2
        )

        boton.grid(row=fila, column=columna)

ventana.mainloop()

def comprobar_ganador(tablero, jugador):

    # Comprobar filas
    for fila in tablero:
        if fila[0] == jugador and fila[1] == jugador and fila[2] == jugador:
            return True

    # Comprobar columnas
    for columna in range(3):
        if (tablero[0][columna] == jugador and
            tablero[1][columna] == jugador and
            tablero[2][columna] == jugador):
            return True

    # Comprobar diagonal \
    if (tablero[0][0] == jugador and
        tablero[1][1] == jugador and
        tablero[2][2] == jugador):
        return True

    # Comprobar diagonal /
    if (tablero[0][2] == jugador and
        tablero[1][1] == jugador and
        tablero[2][0] == jugador):
        return True

    return False


def tablero_lleno(tablero):

    for fila in tablero:
        for casilla in fila:
            if casilla == " ":
                return False

    return True


# Crear tablero
tablero = [
    [" ", " ", " "],
    [" ", " ", " "],
    [" ", " ", " "]
]

jugador = "X"

while True:

    posicion = input(
        f"Jugador {jugador}, elige una casilla (ejemplo A1): "
    ).strip().upper()

    # Comprobar que la entrada tenga exactamente 2 caracteres
    if len(posicion) != 2:
        print("❌ Entrada inválida. Debes escribir algo como A1.")
        continue

    # Comprobar que la fila sea A, B o C
    if posicion[0] not in "ABC":
        print("❌ La fila debe ser A, B o C.")
        continue

    # Comprobar que la columna sea 1, 2 o 3
    if posicion[1] not in "123":
        print("❌ La columna debe ser 1, 2 o 3.")
        continue

    # Convertir la posición a índices
    fila = ord(posicion[0]) - ord("A")
    columna = int(posicion[1]) - 1

    # Comprobar si la casilla está ocupada
    if tablero[fila][columna] != " ":
        print("❌ Esa casilla ya está ocupada.")
        continue

    # Colocar ficha
    tablero[fila][columna] = jugador

    # Mostrar tablero
    print()
    print("   1   2   3")
    print("A  " + tablero[0][0] + " | " + tablero[0][1] + " | " + tablero[0][2])
    print("  ---+---+---")
    print("B  " + tablero[1][0] + " | " + tablero[1][1] + " | " + tablero[1][2])
    print("  ---+---+---")
    print("C  " + tablero[2][0] + " | " + tablero[2][1] + " | " + tablero[2][2])
    print()

    # Comprobar ganador
    if comprobar_ganador(tablero, jugador):
        print(f"🎉 ¡El jugador {jugador} ha ganado!")
        break

    # Comprobar empate
    if tablero_lleno(tablero):
        print("🤝 ¡Empate! El tablero está lleno.")
        break

    # Cambiar jugador
    if jugador == "X":
        jugador = "O"
    else:
        jugador = "X"
