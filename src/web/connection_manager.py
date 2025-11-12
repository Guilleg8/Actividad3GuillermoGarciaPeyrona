
import asyncio
import json
from typing import List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        message = json.dumps(data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

data_queue = asyncio.Queue()


async def websocket_broadcaster():
    print("[WebSocket] Broadcaster iniciado. Esperando eventos...")
    while True:
        try:
            data = await data_queue.get()

            await manager.broadcast(data)

            data_queue.task_done()
        except asyncio.CancelledError:
            print("[WebSocket] Broadcaster detenido.")
            break
        except Exception as e:
            print(f"[WebSocket] Error en broadcaster: {e}")