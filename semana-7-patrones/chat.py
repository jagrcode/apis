from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Chat con WebSockets")
conectados: list[WebSocket] = []


@app.websocket("/ws")
async def sala(websocket: WebSocket):
    await websocket.accept()
    conectados.append(websocket)
    try:
        while True:
            texto = await websocket.receive_text()
            for c in list(conectados):
                await c.send_text(texto)      # lo recibe todo el mundo
    except WebSocketDisconnect:
        conectados.remove(websocket)