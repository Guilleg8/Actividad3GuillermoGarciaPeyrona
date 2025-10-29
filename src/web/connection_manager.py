# src/umbrella_analysis/web/connection_manager.py

import asyncio
import json
from typing import List
from fastapi import WebSocket

"""
Este módulo actúa como el "puente" de comunicación.

1. 'manager' (ConnectionManager): Mantiene una lista de todos los navegadores
   conectados.
2. 'data_queue' (asyncio.Queue): Una cola donde el backend (Orchestrator,
   AlertManager) puede "soltar" eventos.
3. 'websocket_broadcaster': Una tarea que saca eventos de la 'data_queue'
   y los envía a todos los navegadores conectados.
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """Envía datos JSON a todas las conexiones activas."""
        message = json.dumps(data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Manejar desconexiones, etc.
                pass


# Instancia global del manager
manager = ConnectionManager()

# El puente: una cola de asyncio
data_queue = asyncio.Queue()


async def websocket_broadcaster():
    """
    Tarea de fondo que escucha la cola y transmite
    a todos los clientes de WebSocket.
    """
    print("[WebSocket] Broadcaster iniciado. Esperando eventos...")
    while True:
        try:
            # Espera por un nuevo evento de la cola
            data = await data_queue.get()

            # Transmite el evento a todos los clientes conectados
            await manager.broadcast(data)

            data_queue.task_done()
        except asyncio.CancelledError:
            print("[WebSocket] Broadcaster detenido.")
            break
        except Exception as e:
            print(f"[WebSocket] Error en broadcaster: {e}")