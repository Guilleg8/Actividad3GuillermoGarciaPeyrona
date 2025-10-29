# src/umbrella_analysis/processing/__init__.py

"""
Módulo de Procesamiento Concurrente

Contiene el orquestador principal y las definiciones de tareas
CPU-bound e I/O-bound.
"""

from .orchestrator import DataOrchestrator

__all__ = [
    "DataOrchestrator"
]