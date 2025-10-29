# src/umbrella_analysis/services/fisico_service.py

from typing import Any, Dict
from .base_service import BaseDataService


class FisicoService(BaseDataService):
    """
    Servicio especializado para el análisis de datos físicos (signos vitales).
    Hereda de BaseDataService e implementa la lógica de alerta específica.
    """

    MAX_HEART_RATE = 190
    MIN_HEART_RATE = 40
    MIN_SPO2 = 90  # Saturación de oxígeno

    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:
        """
        Verifica si los signos vitales indican un evento crítico.

        Args:
            data (Dict[str, Any]): Datos físicos normalizados.
                                   Se espera un formato como:
                                   {'subject_id': '...', 'heart_rate': 70,
                                    'spo2': 98}

        Returns:
            bool: True si se detecta un signo vital crítico.
        """
        #  Lógica de alerta inmediata
        heart_rate = data.get("heart_rate")
        spo2 = data.get("spo2")

        if heart_rate is not None:
            if heart_rate > self.MAX_HEART_RATE or heart_rate < self.MIN_HEART_RATE:
                return True

        if spo2 is not None and spo2 < self.MIN_SPO2:
            return True

        # Caso especial: paro cardíaco
        if heart_rate == 0:
            return True

        return False