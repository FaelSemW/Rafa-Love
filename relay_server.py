from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from collections import defaultdict
import json

app = FastAPI()
rooms: dict[str, set[WebSocket]] = defaultdict(set)

@app.get("/")
def root():
    return {"ok": True}

@app.get("/stats")
def stats():
    return {"rooms": {room: len(clients) for room, clients in rooms.items()}}

@app.post("/ping")
async def ping(payload: dict = Body(...)):
    room = str(payload.get("room", "love"))

    text = json.dumps(payload, ensure_ascii=False)

    dead = []
    for client in list(rooms[room]):
        try:
            await client.send_text(text)
        except:
            dead.append(client)

    for d in dead:
        rooms[room].discard(d)

    return {"ok": True, "room": room, "sent_to": len(rooms[room])}

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
