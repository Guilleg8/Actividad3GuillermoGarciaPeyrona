
from typing import Any, Dict
from .base_service import BaseDataService


class FisicoService(BaseDataService):

    MAX_HEART_RATE = 190
    MIN_HEART_RATE = 40
    MIN_SPO2 = 90

    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:

        heart_rate = data.get("heart_rate")
        spo2 = data.get("spo2")

        if heart_rate is not None:
            if heart_rate > self.MAX_HEART_RATE or heart_rate < self.MIN_HEART_RATE:
                return True

        if spo2 is not None and spo2 < self.MIN_SPO2:
            return True

        if heart_rate == 0:
            return True

        return False