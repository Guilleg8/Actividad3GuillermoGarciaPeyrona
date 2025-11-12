
import time
from typing import Dict, Any


def _simulate_heavy_computation(duration_sec: float):
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time) < duration_sec:
        _ = 1 + 1


def analyze_genetic_sequence(data: Dict[str, Any]) -> Dict[str, Any]:
    sample_id = data.get('sample_id', 'unknown')
    sequence = data.get('sequence', '')

    _simulate_heavy_computation(2.0)

    result = {
        "analysis_id": f"res_{sample_id}",
        "source_data": data,
        "finding": "Mutación T-Virus detectada" if "T" in sequence else "Estable",
        "analysis_type": "genetic"
    }
    return result


def analyze_biochemical_model(data: Dict[str, Any]) -> Dict[str, Any]:
    sample_id = data.get('sample_id', 'unknown')

    _simulate_heavy_computation(1.5)

    result = {
        "analysis_id": f"res_{sample_id}",
        "source_data": data,
        "finding": "Niveles de toxina inestables",
        "analysis_type": "biochemical"
    }
    return result