from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from collections import defaultdict

app = FastAPI()
rooms: dict[str, set[WebSocket]] = defaultdict(set)


@app.get("/")
def root():
    return {"ok": True}


@app.get("/stats")
def stats():
    return {"rooms": {room: len(clients) for room, clients in rooms.items()}}


@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    await ws.accept()
    rooms[room].add(ws)

    try:
        while True:
            msg = await ws.receive_text()

            dead = []
            for client in list(rooms[room]):
                try:
                    await client.send_text(msg)
                except:
                    dead.append(client)

            for d in dead:
                rooms[room].discard(d)

    except WebSocketDisconnect:
        rooms[room].discard(ws)
