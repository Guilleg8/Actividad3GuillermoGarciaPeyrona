# src/web/app.py

import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# --- Arreglo de Importación ---
# (Asegúrate de que estas importaciones NO tengan '..' o 'umbrella_analysis')
from monitoring import MetricsCollector
from .connection_manager import manager, websocket_broadcaster

# ---------------------------

# --- Arreglo del Primer Error ---
# (Esto corrige el 'FastAPI(...)')
app = FastAPI(
    title="Umbrella Analysis Dashboard",
    description="Monitorización en tiempo real del sistema de análisis."
)
# ------------------------------

base_dir = Path(__file__).resolve().parent
static_dir = base_dir / "static"
templates_dir = base_dir / "templates"

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)
metrics_collector = MetricsCollector()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(websocket_broadcaster())


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/metrics")
async def get_metrics():
    stats = metrics_collector.get_current_stats()
    return stats


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# --- Arreglo del Segundo Error ---
# (Esto corrige el 'Config(...)')
async def run_web_server():
    """
    Inicia el servidor web Uvicorn de forma programática.
    """
    import uvicorn

    config = uvicorn.Config(
        app,  # <--- Ya no es '...'
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)

    print("[Web Server] Iniciado en http://0.0.0.0:8000")
    await server.serve()
# ---------------------------------