
import asyncio
import time
from typing import Dict, Any


async def save_analysis_to_db_async(result: Dict[str, Any]):

    analysis_id = result.get('analysis_id', 'unknown')
    print(f"    [I/O-Async] Guardando resultado {analysis_id} en BBDD...")

    await asyncio.sleep(0.5)

    print(f"    [I/O-Async] Resultado {analysis_id} guardado.")


def save_vitals_to_file_sync(data: Dict[str, Any]):

    subject_id = data.get('subject_id', 'unknown')

    try:
        time.sleep(0.5)

    except Exception as e:
        print(f"    [I/O-Thread] Error al escribir log: {e}")

