
"""
Módulo de Comunicación

Este módulo centraliza la instanciación de los canales
de comunicación (colas) y eventos de sincronización
que conectan los diferentes componentes del sistema.
"""

from .queues import (
    genetic_input_queue,
    biochemical_input_queue,
    physical_input_queue,
    processing_queue
)

__all__ = [
    # Colas
    "genetic_input_queue",
    "biochemical_input_queue",
    "physical_input_queue",
    "processing_queue",

]