# src/umbrella_analysis/ingestion/__init__.py

"""
Módulo de Ingesta de Datos

Contiene corutinas que simulan la llegada de flujos de datos
externos y los colocan en las colas de procesamiento.
"""

from .data_fetchers import (
    simulate_genetic_data_feed,
    simulate_biochemical_data_feed,
    simulate_physical_data_feed
)

__all__ = [
    "simulate_genetic_data_feed",
    "simulate_biochemical_data_feed",
    "simulate_physical_data_feed"
]