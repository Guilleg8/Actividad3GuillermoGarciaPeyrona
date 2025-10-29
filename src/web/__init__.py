# src/umbrella_analysis/web/__init__.py

"""
Módulo del Servidor Web (Dashboard)

Contiene la aplicación FastAPI, las plantillas HTML
y los activos estáticos (CSS/JS) para el dashboard
de monitorización en tiempo real.
"""

from .app import run_web_server

__all__ = [
    "run_web_server"
]