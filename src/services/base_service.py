import asyncio
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, Dict

# Importaciones de otros módulos (asumimos que existen)
from normalization.validators import DataNormalizer
from alerting.alert_manager import AlertManager
from monitoring import MetricsCollector

class BaseDataService(ABC):

    def __init__(
            self,
            input_queue: Queue,
            processing_queue: Queue,
            normalizer: DataNormalizer,
            alert_manager: AlertManager
    ):

        self.input_queue = input_queue
        self.processing_queue = processing_queue
        self.normalizer = normalizer
        self.alert_manager = alert_manager
        self._is_running = False
        self.metrics = MetricsCollector()  # <--- AÑADE ESTA LÍNEA

    @abstractmethod
    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:

        pass

    async def _process_data(self, raw_data: Any):
        try:
            normalized_data = self.normalizer.normalize(raw_data)

            self.metrics.record_event(normalized_data.get("type", "unknown"))

            if self._check_for_critical_events(normalized_data):
                await self.alert_manager.send_alert(
                    level="CRITICAL",
                    message=f"Evento crítico detectado en {self.__class__.__name__}",
                    data=normalized_data
                )

            await self.processing_queue.put(normalized_data)

        except ValueError as e:
            print(f"Error de validación en {self.__class__.__name__}: {e}")
        except Exception as e:
            print(f"Error inesperado procesando datos: {e}")

    async def start(self):

        self._is_running = True
        print(f"Iniciando {self.__class__.__name__}...")
        while self._is_running:
            try:
                raw_data = await self.input_queue.get()

                await self._process_data(raw_data)

                self.input_queue.task_done()
            except asyncio.CancelledError:
                print(f"Deteniendo {self.__class__.__name__}...")
                self._is_running = False

    def stop(self):

        self._is_running = False