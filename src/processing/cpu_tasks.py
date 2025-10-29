# src/umbrella_analysis/processing/cpu_tasks.py

import time
from typing import Dict, Any


def _simulate_heavy_computation(duration_sec: float):
    # ... (esta función se queda igual) ...
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time) < duration_sec:
        _ = 1 + 1


def analyze_genetic_sequence(data: Dict[str, Any]) -> Dict[str, Any]:
    sample_id = data.get('sample_id', 'unknown')
    sequence = data.get('sequence', '')
    # print(f"  [CPU-Process] Analizando secuencia genética de {sample_id}...") # <--- ELIMINA ESTA LÍNEA

    _simulate_heavy_computation(2.0)

    result = {
        "analysis_id": f"res_{sample_id}",
        "source_data": data,
        "finding": "Mutación T-Virus detectada" if "T" in sequence else "Estable",
        "analysis_type": "genetic"
    }
    # print(f"  [CPU-Process] Análisis de {sample_id} completo.") # <--- ELIMINA ESTA LÍNEA
    return result


def analyze_biochemical_model(data: Dict[str, Any]) -> Dict[str, Any]:
    sample_id = data.get('sample_id', 'unknown')
    # print(f"  [CPU-Process] Simulando modelo bioquímico de {sample_id}...") # <--- ELIMINA ESTA LÍNEA

    _simulate_heavy_computation(1.5)

    result = {
        "analysis_id": f"res_{sample_id}",
        "source_data": data,
        "finding": "Niveles de toxina inestables",
        "analysis_type": "biochemical"
    }
    # print(f"  [CPU-Process] Simulación de {sample_id} completa.") # <--- ELIMINA ESTA LÍNEA
    return result