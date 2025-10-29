# src/umbrella_analysis/monitoring/__init__.py

"""
Módulo de Monitorización y Métricas

Expone el colector de métricas Singleton.
"""

from .metrics import MetricsCollector

__all__ = [
    "MetricsCollector"
]