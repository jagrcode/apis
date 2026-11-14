import tkinter as tk
from tkinter import messagebox


# ==========================================
# CONFIGURACIÓN
# ==========================================

tablero = [
    [" ", " ", " "],
    [" ", " ", " "],
    [" ", " ", " "]
]

jugador = "X"

botones = []

partida_terminada = False


# ==========================================
# COMPROBAR GANADOR
# ==========================================

def comprobar_ganador(jugador):

    # Filas
    for fila in range(3):
        if (
            tablero[fila][0] == jugador and
            tablero[fila][1] == jugador and
            tablero[fila][2] == jugador
        ):
            return [
                (fila, 0),
                (fila, 1),
                (fila, 2)
            ]

    # Columnas
    for columna in range(3):
        if (
            tablero[0][columna] == jugador and
            tablero[1][columna] == jugador and
            tablero[2][columna] == jugador
        ):
            return [
                (0, columna),
                (1, columna),
                (2, columna)
            ]

    # Diagonal \
    if (
        tablero[0][0] == jugador and
        tablero[1][1] == jugador and
        tablero[2][2] == jugador
    ):
        return [
            (0, 0),
            (1, 1),
            (2, 2)
        ]

    # Diagonal /
    if (
        tablero[0][2] == jugador and
        tablero[1][1] == jugador and
        tablero[2][0] == jugador
    ):
        return [
            (0, 2),
            (1, 1),
            (2, 0)
        ]

    return None


# ==========================================
# COMPROBAR EMPATE
# ==========================================

def tablero_lleno():

    for fila in tablero:
        for casilla in fila:
            if casilla == " ":
                return False

    return True


# ==========================================
# ANIMACIÓN DE VICTORIA
# ==========================================

def animar_ganador(casillas, estado=False, veces=0):

    if veces >= 8:
        for fila, columna in casillas:
            botones[fila][columna].config(
                bg="#22c55e",
                fg="white"
            )
        return

    if estado:
        color = "#22c55e"
    else:
        color = "#14532d"

    for fila, columna in casillas:
        botones[fila][columna].config(bg=color)

    ventana.after(
        250,
        lambda: animar_ganador(
            casillas,
            not estado,
            veces + 1
        )
    )


# ==========================================
# ANIMACIÓN DE LA FICHA
# ==========================================

def animar_ficha(boton, jugador, tamaño=10):

    if tamaño >= 32:

        boton.config(
            font=("Arial", 32, "bold")
        )

        return

    boton.config(
        font=("Arial", tamaño, "bold")
    )

    ventana.after(
        15,
        lambda: animar_ficha(
            boton,
            jugador,
            tamaño + 2
        )
    )


# ==========================================
# JUGAR
# ==========================================

def jugar(fila, columna):

    global jugador
    global partida_terminada

    if partida_terminada:
        return

    # Casilla ocupada
    if tablero[fila][columna] != " ":
        return

    # Guardar movimiento
    tablero[fila][columna] = jugador

    boton = botones[fila][columna]

    # Mostrar ficha
    boton.config(
        text=jugador,
        fg="#38bdf8" if jugador == "X" else "#fb7185"
    )

    # Animación
    animar_ficha(boton, jugador)

    # Comprobar ganador
    ganador = comprobar_ganador(jugador)

    if ganador:

        partida_terminada = True

        etiqueta_turno.config(
            text=f"🏆 ¡Ganó el jugador {jugador}!",
            fg="#22c55e"
        )

        # Animar las tres casillas ganadoras
        animar_ganador(ganador)

        ventana.after(
            2200,
            lambda: mostrar_ganador(jugador)
        )

        return

    # Comprobar empate
    if tablero_lleno():

        partida_terminada = True

        etiqueta_turno.config(
            text="🤝 ¡Empate!",
            fg="#facc15"
        )

        ventana.after(
            500,
            lambda: messagebox.showinfo(
                "Tres en Raya",
                "🤝 ¡La partida terminó en empate!"
            )
        )

        return

    # Cambiar jugador
    if jugador == "X":
        jugador = "O"
    else:
        jugador = "X"

    etiqueta_turno.config(
        text=f"Turno del jugador: {jugador}",
        fg="#38bdf8" if jugador == "X" else "#fb7185"
    )


# ==========================================
# MENSAJE DE GANADOR
# ==========================================

def mostrar_ganador(ganador):

    messagebox.showinfo(
        "¡Tenemos ganador!",
        f"🎉 ¡El jugador {ganador} ha ganado!"
    )


# ==========================================
# REINICIAR
# ==========================================

def reiniciar():

    global jugador
    global partida_terminada

    jugador = "X"
    partida_terminada = False

    # Limpiar tablero
    for fila in range(3):

        for columna in range(3):

            tablero[fila][columna] = " "

            botones[fila][columna].config(
                text="",
                bg="#1e293b",
                fg="white",
                state="normal",
                font=("Arial", 32, "bold")
            )

    etiqueta_turno.config(
        text="Turno del jugador: X",
        fg="#38bdf8"
    )


# ==========================================
# VENTANA
# ==========================================

ventana = tk.Tk()

ventana.title("Tres en Raya")

# Un poco más alta para que no se corte
ventana.geometry("460x650")

# No permitir que el usuario la haga demasiado pequeña
ventana.minsize(460, 650)

ventana.configure(
    bg="#0f172a"
)


# ==========================================
# TÍTULO
# ==========================================

titulo = tk.Label(
    ventana,
    text="TRES EN RAYA",
    font=("Arial", 28, "bold"),
    bg="#0f172a",
    fg="white"
)

titulo.pack(pady=(25, 5))


subtitulo = tk.Label(
    ventana,
    text="❌  VS  ⭕",
    font=("Arial", 15),
    bg="#0f172a",
    fg="#94a3b8"
)

subtitulo.pack(pady=(0, 15))


# ==========================================
# TURNO
# ==========================================

etiqueta_turno = tk.Label(
    ventana,
    text="Turno del jugador: X",
    font=("Arial", 17, "bold"),
    bg="#0f172a",
    fg="#38bdf8"
)

etiqueta_turno.pack(pady=10)


# ==========================================
# TABLERO
# ==========================================

marco_tablero = tk.Frame(
    ventana,
    bg="#020617",
    padx=8,
    pady=8
)

marco_tablero.pack(pady=15)


# Crear los botones
for fila in range(3):

    fila_botones = []

    for columna in range(3):

        boton = tk.Button(
            marco_tablero,
            text="",
            font=("Arial", 32, "bold"),
            width=4,
            height=2,

            bg="#1e293b",
            fg="white",

            activebackground="#334155",

            relief="flat",
            bd=0,

            command=lambda f=fila, c=columna:
                jugar(f, c)
        )

        boton.grid(
            row=fila,
            column=columna,
            padx=5,
            pady=5
        )

        fila_botones.append(boton)

    botones.append(fila_botones)


# ==========================================
# INFORMACIÓN
# ==========================================

instrucciones = tk.Label(
    ventana,
    text="Haz clic en una casilla para jugar",
    font=("Arial", 12),
    bg="#0f172a",
    fg="#94a3b8"
)

instrucciones.pack(pady=(10, 15))


# ==========================================
# BOTÓN REINICIAR
# ==========================================

boton_reiniciar = tk.Button(
    ventana,
    text="🔄  NUEVA PARTIDA",
    font=("Arial", 14, "bold"),

    bg="#2563eb",
    fg="white",

    activebackground="#1d4ed8",
    activeforeground="white",

    relief="flat",
    bd=0,

    padx=25,
    pady=12,

    cursor="hand2",

    command=reiniciar
)

boton_reiniciar.pack(pady=10)


# ==========================================
# EJECUTAR
# ==========================================

ventana.mainloop()
