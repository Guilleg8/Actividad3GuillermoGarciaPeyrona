# tests/test_monitoring.py

import pytest
from umbrella_analysis.monitoring import MetricsCollector


@pytest.fixture
def metrics_collector():
    """
    Fixture que obtiene la instancia del collector y la limpia
    antes de cada prueba para evitar contaminación entre tests.
    """
    collector = MetricsCollector()

    # --- Resetear estado antes de la prueba ---
    with collector.events_lock, collector.errors_lock, collector.latency_lock, collector.alert_lock:
        collector.events_processed = {
            "total": 0, "genetic": 0, "biochemical": 0, "physical": 0
        }
        collector.errors_count = {
            "total": 0, "validation": 0, "processing": 0
        }
        collector.processing_stats = {
            "genetic": {"sum_ms": 0.0, "count": 0},
            "biochemical": {"sum_ms": 0.0, "count": 0}
        }
        collector.alert_stats = {"sum_ms": 0.0, "count": 0}

    return collector


def test_metrics_is_singleton():
    """Prueba que múltiples 'construcciones' devuelven la misma instancia."""
    m1 = MetricsCollector()
    m2 = MetricsCollector()

    assert m1 is m2, "MetricsCollector no está devolviendo la misma instancia"


def test_record_event(metrics_collector):
    """Prueba el contador de eventos."""
    metrics_collector.record_event("genetic")
    metrics_collector.record_event("genetic")
    metrics_collector.record_event("physical")

    stats = metrics_collector.get_current_stats()

    assert stats["events_processed"]["total"] == 3
    assert stats["events_processed"]["genetic"] == 2
    assert stats["events_processed"]["physical"] == 1
    assert stats["events_processed"]["biochemical"] == 0


def test_record_error(metrics_collector):
    """Prueba el contador de errores."""
    metrics_collector.record_error("validation")

    stats = metrics_collector.get_current_stats()

    assert stats["errors_count"]["total"] == 1
    assert stats["errors_count"]["validation"] == 1
    assert stats["errors_count"]["processing"] == 0


def test_average_processing_latency(metrics_collector):
    """Prueba el cálculo del promedio de latencia."""
    metrics_collector.record_processing_time("genetic", 100.0)  # 100ms
    metrics_collector.record_processing_time("genetic", 200.0)  # 200ms

    stats = metrics_collector.get_current_stats()

    # Promedio (100 + 200) / 2 = 150
    assert stats["average_processing_latency_ms"]["genetic"] == 150.0
    assert stats["average_processing_latency_ms"]["biochemical"] == 0.0


def test_average_latency_no_data(metrics_collector):
    """Prueba que el promedio es 0.0 si no hay datos (evita división por cero)."""
    stats = metrics_collector.get_current_stats()

    assert stats["average_processing_latency_ms"]["genetic"] == 0.0
    assert stats["average_alert_latency_ms"] == 0.0