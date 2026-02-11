from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from collections import defaultdict

app = FastAPI()
rooms = defaultdict(set)

@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    await ws.accept()
    rooms[room].add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for client in rooms[room]:
                await client.send_text(msg)
    except WebSocketDisconnect:
        rooms[room].remove(ws)
