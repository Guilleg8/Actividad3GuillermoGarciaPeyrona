# run.py
import asyncio
import sys
import os
import multiprocessing

# --- INICIO DEL HACK PARA OCULTAR VENTANAS EN WINDOWS ---
if sys.platform == "win32":
    pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if os.path.exists(pythonw_exe):
        multiprocessing.set_executable(pythonw_exe)
        print("[Launcher] Configurado para ocultar ventanas de procesos hijos (usando pythonw.exe).")
# --- FIN DEL HACK ---


# --- ESTA PARTE ARREGLA TUS IMPORTACIONES ---
# Añade el directorio 'src' al path de Python
# para que podamos importar 'main', 'web', 'processing', etc.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    # Importamos directamente 'main' y 'web', NO 'src.main'
    from main import main as run_backend
    from web import run_web_server
except ModuleNotFoundError as e:
    print(f"Error: No se pudo importar el módulo. ¿Estás seguro que 'src' existe?")
    print(f"Detalle: {e}")
    sys.exit(1)


# -------------------------------------


async def start_system():
    """
    Inicia y ejecuta concurrentemente el backend de análisis
    y el servidor web del dashboard.
    """
    print("[Launcher] Iniciando todos los sistemas...")

    backend_task = asyncio.create_task(run_backend())
    web_server_task = asyncio.create_task(run_web_server())

    await asyncio.gather(backend_task, web_server_task)


if __name__ == "__main__":
    try:
        asyncio.run(start_system())
    except KeyboardInterrupt:
        print("\n[Launcher] Apagado solicitado por el usuario (Ctrl+C).")
    except Exception as e:
        print(f"\n[Launcher] Error crítico: {e}")
    finally:
        print("[Launcher] Sistema detenido.")