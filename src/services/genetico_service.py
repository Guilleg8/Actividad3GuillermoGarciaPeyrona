
from typing import Any, Dict
from .base_service import BaseDataService


class GeneticoService(BaseDataService):


    CRITICAL_MUTATIONS = {"T-VIRUS", "G-VIRUS"}

    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:

        detected_mutations = data.get("detected_mutations", set())

        if not isinstance(detected_mutations, set):
            detected_mutations = set(detected_mutations)

        if self.CRITICAL_MUTATIONS.intersection(detected_mutations):
            return True

        return False