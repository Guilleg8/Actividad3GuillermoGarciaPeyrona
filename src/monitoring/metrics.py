
import threading
import time
from typing import Any, Dict, List


class MetricsCollector:

    _instance: Any = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):

        self.events_lock = threading.Lock()
        self.errors_lock = threading.Lock()
        self.latency_lock = threading.Lock()
        self.alert_lock = threading.Lock()

        self.events_processed: Dict[str, int] = {
            "total": 0,
            "genetic": 0,
            "biochemical": 0,
            "physical": 0
        }

        self.errors_count: Dict[str, int] = {
            "total": 0,
            "validation": 0,
            "processing": 0
        }

        self.processing_stats: Dict[str, Dict[str, Any]] = {
            "genetic": {"sum_ms": 0.0, "count": 0},
            "biochemical": {"sum_ms": 0.0, "count": 0},
            "physical": {"sum_ms": 0.0, "count": 0}
        }

        self.alert_stats: Dict[str, Any] = {"sum_ms": 0.0, "count": 0}


    def record_event(self, event_type: str):

        with self.events_lock:
            self.events_processed["total"] += 1
            if event_type in self.events_processed:
                self.events_processed[event_type] += 1

    def record_error(self, error_type: str = "processing"):

        with self.errors_lock:
            self.errors_count["total"] += 1
            if error_type in self.errors_count:
                self.errors_count[error_type] += 1

    def record_processing_time(self, data_type: str, duration_ms: float):

        with self.latency_lock:
            if data_type in self.processing_stats:
                stats = self.processing_stats[data_type]
                stats["sum_ms"] += duration_ms
                stats["count"] += 1

    def record_alert_latency(self, start_time: float):

        duration_ms = (time.perf_counter() - start_time) * 1000
        with self.alert_lock:
            self.alert_stats["sum_ms"] += duration_ms
            self.alert_stats["count"] += 1


    def get_current_stats(self) -> Dict[str, Any]:

        with self.events_lock, self.errors_lock, self.latency_lock, self.alert_lock:
            events = self.events_processed.copy()
            errors = self.errors_count.copy()

            avg_processing = {}
            for dtype, stats in self.processing_stats.items():
                count = stats['count']
                avg_processing[dtype] = (stats['sum_ms'] / count) if count > 0 else 0.0

            alert_count = self.alert_stats['count']
            avg_alert = (self.alert_stats['sum_ms'] / alert_count) if alert_count > 0 else 0.0

            return {
                "events_processed": events,
                "errors_count": errors,
                "average_processing_latency_ms": avg_processing,
                "average_alert_latency_ms": avg_alert
            }