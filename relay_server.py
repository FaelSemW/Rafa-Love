from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from collections import defaultdict

app = FastAPI()
rooms: dict[str, set[WebSocket]] = defaultdict(set)

@app.post("/ping")
async def ping(payload: dict = Body(...)):
    """
    Recebe um POST e repassa como texto para todos os clientes conectados
    no WebSocket da sala /ws/{room}.
    """
    room = str(payload.get("room", "love"))
    msg = payload.get("message", "")

    # Se quiser mandar o payload inteiro pro receiver (recomendado):
    # o receiver pode mostrar notificação com base nisso.
    import json
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

