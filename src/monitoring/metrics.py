# src/umbrella_analysis/monitoring/metrics.py

import threading
import time
from typing import Any, Dict, List


class MetricsCollector:
    """
    Un colector de métricas Singleton y thread-safe para monitorizar
    la salud y el rendimiento del sistema.

    Almacena contadores de eventos, errores y estadísticas de latencia.
    """

    # --- Implementación del Singleton ---
    _instance: Any = None
    _lock = threading.Lock()  # Lock para la creación del singleton

    def __new__(cls, *args, **kwargs):
        # Asegura que solo se cree una instancia
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # --- Fin del Singleton ---

    def __init__(self):
        """
        Inicializa los almacenes de métricas.
        Este __init__ se ejecutará solo una vez.
        """
        # Usamos locks separados para cada sección de datos
        # para permitir lecturas/escrituras concurrentes en
        # diferentes tipos de métricas (granularidad fina).
        self.events_lock = threading.Lock()
        self.errors_lock = threading.Lock()
        self.latency_lock = threading.Lock()
        self.alert_lock = threading.Lock()

        # --- Almacenes de Métricas ---

        self.events_processed: Dict[str, int] = {
            "total": 0,
            "genetic": 0,
            "biochemical": 0,
            "physical": 0
        }

        self.errors_count: Dict[str, int] = {
            "total": 0,
            "validation": 0,  # Errores de normalización
            "processing": 0  # Errores en el orchestrator
        }

        # Almacenamos suma y contador para calcular el promedio
        self.processing_stats: Dict[str, Dict[str, Any]] = {
            "genetic": {"sum_ms": 0.0, "count": 0},
            "biochemical": {"sum_ms": 0.0, "count": 0},
            "physical": {"sum_ms": 0.0, "count": 0}
        }

        self.alert_stats: Dict[str, Any] = {"sum_ms": 0.0, "count": 0}

    # --- Métodos para registrar métricas (Escritura) ---

    def record_event(self, event_type: str):
        """
        Incrementa el contador para un tipo de evento procesado.
        Llamado por los 'Services' tras la normalización.
        """
        with self.events_lock:
            self.events_processed["total"] += 1
            if event_type in self.events_processed:
                self.events_processed[event_type] += 1

    def record_error(self, error_type: str = "processing"):
        """
        Incrementa el contador para un tipo de error.
        Ej. 'validation' (de Normalizer), 'processing' (de Orchestrator)
        """
        with self.errors_lock:
            self.errors_count["total"] += 1
            if error_type in self.errors_count:
                self.errors_count[error_type] += 1

    def record_processing_time(self, data_type: str, duration_ms: float):
        """
        Registra la duración de una tarea de procesamiento (CPU-bound).
        Llamado por el 'Orchestrator' cuando una tarea del pool finaliza.
        """
        with self.latency_lock:
            if data_type in self.processing_stats:
                stats = self.processing_stats[data_type]
                stats["sum_ms"] += duration_ms
                stats["count"] += 1

    def record_alert_latency(self, start_time: float):
        """
        Registra la latencia desde la detección hasta el envío de la alerta.
        Llamado por el 'AlertManager' cuando la alerta ha sido enviada.
        """
        duration_ms = (time.perf_counter() - start_time) * 1000
        with self.alert_lock:
            self.alert_stats["sum_ms"] += duration_ms
            self.alert_stats["count"] += 1

    # --- Métodos para obtener métricas (Lectura) ---

    def get_current_stats(self) -> Dict[str, Any]:
        """
        Obtiene una instantánea (snapshot) de todas las métricas actuales.
        Este método es el que llamará la API del dashboard (web/app.py).
        """
        # Adquirimos todos los locks para asegurar una instantánea consistente
        with self.events_lock, self.errors_lock, self.latency_lock, self.alert_lock:
            # 1. Copiar contadores
            events = self.events_processed.copy()
            errors = self.errors_count.copy()

            # 2. Calcular promedios de procesamiento
            avg_processing = {}
            for dtype, stats in self.processing_stats.items():
                count = stats['count']
                avg_processing[dtype] = (stats['sum_ms'] / count) if count > 0 else 0.0

            # 3. Calcular promedio de alertas
            alert_count = self.alert_stats['count']
            avg_alert = (self.alert_stats['sum_ms'] / alert_count) if alert_count > 0 else 0.0

            return {
                "events_processed": events,
                "errors_count": errors,
                "average_processing_latency_ms": avg_processing,
                "average_alert_latency_ms": avg_alert
            }