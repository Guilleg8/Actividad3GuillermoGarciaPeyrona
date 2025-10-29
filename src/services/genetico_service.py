# src/umbrella_analysis/services/genetico_service.py

from typing import Any, Dict
from .base_service import BaseDataService


class GeneticoService(BaseDataService):
    """
    Servicio especializado para el análisis de datos genéticos.
    Hereda de BaseDataService e implementa la lógica de alerta específica.
    """

    CRITICAL_MUTATIONS = {"T-VIRUS", "G-VIRUS"}  # Ejemplo de mutaciones críticas

    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:
        """
        Verifica si se ha detectado una mutación genética crítica.

        Args:
            data (Dict[str, Any]): Datos genéticos normalizados.
                                   Se espera un formato como:
                                   {'sample_id': '...', 'sequence': '...',
                                    'detected_mutations': ['...']}

        Returns:
            bool: True si se detecta una mutación crítica.
        """
        #  Lógica de alerta inmediata
        detected_mutations = data.get("detected_mutations", set())

        if not isinstance(detected_mutations, set):
            detected_mutations = set(detected_mutations)

        # Comprueba si alguna mutación crítica está en las detectadas
        if self.CRITICAL_MUTATIONS.intersection(detected_mutations):
            return True

        return False