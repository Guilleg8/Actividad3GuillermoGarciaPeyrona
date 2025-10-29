# src/umbrella_analysis/services/bioquimico_service.py

from typing import Any, Dict
from .base_service import BaseDataService


class BioquimicoService(BaseDataService):
    """
    Servicio especializado para el análisis de datos bioquímicos.
    Hereda de BaseDataService e implementa la lógica de alerta específica.
    """

    # Umbrales críticos de ejemplo
    TOXIN_THRESHOLD = 80.0  # Nivel de toxina por encima del cual alertar
    PROTEIN_X_MIN = 5.0  # Nivel mínimo de proteína estabilizadora

    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:
        """
        Verifica si los niveles bioquímicos están en rangos críticos.

        Args:
            data (Dict[str, Any]): Datos bioquímicos normalizados.
                                   Se espera un formato como:
                                   {'sample_id': '...', 'toxin_level': 75.5,
                                    'protein_x_level': 2.1}

        Returns:
            bool: True si se detecta un nivel crítico.
        """
        #  Lógica de alerta inmediata
        toxin_level = data.get("toxin_level", 0.0)
        protein_x = data.get("protein_x_level", 10.0)

        if toxin_level > self.TOXIN_THRESHOLD:
            return True

        if protein_x < self.PROTEIN_X_MIN:
            return True

        return False