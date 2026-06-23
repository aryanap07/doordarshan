# Main FastAPI application for doordarshan.
# Defines HTTP and WebSocket routes required by the application.
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to doordarshan"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    print(f"Client connected to room: {room_id}")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        print(f"Client disconnected from room: {room_id}")
