# src/umbrella_analysis/communication/queues.py

import asyncio

# --- Colas de Ingesta (Ingestor -> Servicio) ---
# Estas colas reciben datos crudos de los simuladores.

genetic_input_queue = asyncio.Queue(maxsize=100)
"""Cola para datos genéticos crudos."""

biochemical_input_queue = asyncio.Queue(maxsize=100)
"""Cola para datos bioquímicos crudos."""

physical_input_queue = asyncio.Queue(maxsize=100)
"""Cola para datos físicos crudos."""


# --- Cola de Procesamiento (Servicio -> Orquestador) ---
# Esta es la cola principal de trabajo.
# Es más grande porque agrega los 3 flujos de entrada.

processing_queue = asyncio.Queue(maxsize=300)
"""
Cola para datos normalizados y validados, listos para 
el procesamiento pesado (CPU/IO) por el Orchestrator.
"""