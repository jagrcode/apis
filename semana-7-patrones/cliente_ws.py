import asyncio
import sys

import websockets

URL = "ws://127.0.0.1:8000/ws"


async def main(nombre):
    async with websockets.connect(URL) as ws:
        await ws.send(f"{nombre} se conectó")
        async for mensaje in ws:
            print(mensaje)


asyncio.run(main(sys.argv[1]))