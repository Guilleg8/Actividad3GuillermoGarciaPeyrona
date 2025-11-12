
from typing import Any, Dict
from .base_service import BaseDataService


class BioquimicoService(BaseDataService):

    TOXIN_THRESHOLD = 80.0
    PROTEIN_X_MIN = 5.0

    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:

        toxin_level = data.get("toxin_level", 0.0)
        protein_x = data.get("protein_x_level", 10.0)

        if toxin_level > self.TOXIN_THRESHOLD:
            return True

        if protein_x < self.PROTEIN_X_MIN:
            return True

        return False