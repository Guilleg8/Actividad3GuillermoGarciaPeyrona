# src/umbrella_analysis/alerting/__init__.py

"""
Módulo de Alertas

Proporciona la clase AlertManager para gestionar el envío
de notificaciones críticas en tiempo real.
"""

from .alert_manager import AlertManager

__all__ = [
    "AlertManager"
]