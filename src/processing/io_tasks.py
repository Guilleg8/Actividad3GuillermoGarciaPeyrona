# src/umbrella_analysis/processing/io_tasks.py

import asyncio
import time
from typing import Dict, Any


async def save_analysis_to_db_async(result: Dict[str, Any]):
    """
    Simula una tarea I/O-bound ASÍNCRONA (no bloqueante).
    Ej. Escribir un resultado en una base de datos (PostgreSQL con asyncpg).
    """
    analysis_id = result.get('analysis_id', 'unknown')
    print(f"    [I/O-Async] Guardando resultado {analysis_id} en BBDD...")

    # asyncio.sleep(0.5) simula una llamada de red no bloqueante
    await asyncio.sleep(0.5)

    print(f"    [I/O-Async] Resultado {analysis_id} guardado.")


def save_vitals_to_file_sync(data: Dict[str, Any]):
    """
    Simula una tarea I/O-bound BLOQUEANTE (síncrona).
    Ej. Escribir datos a un archivo en disco.

    Esta función se ejecuta en un ThreadPoolExecutor para no bloquear
    el hilo principal de asyncio.
    """
    subject_id = data.get('subject_id', 'unknown')

    # time.sleep(0.2) simula la latencia de escritura en disco
    # En un hilo separado, este bloqueo no afecta al loop de asyncio.
    try:
        # Simulación de escritura
        time.sleep(0.5)
        # f = open(f"/tmp/{subject_id}_vitals.log", "a")
        # f.write(str(data) + "\n")
        # f.close()
    except Exception as e:
        print(f"    [I/O-Thread] Error al escribir log: {e}")

