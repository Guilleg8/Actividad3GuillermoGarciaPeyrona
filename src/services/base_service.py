# src/umbrella_analysis/services/base_service.py
import asyncio
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, Dict

# Importaciones de otros módulos (asumimos que existen)
from normalization.validators import DataNormalizer
from alerting.alert_manager import AlertManager
from monitoring import MetricsCollector

class BaseDataService(ABC):
    """
    Clase base abstracta para un servicio de procesamiento de datos.

    Define la interfaz común que seguirán todos los servicios específicos
    (Genético, Bioquímico, Físico).
    """

    def __init__(
            self,
            input_queue: Queue,
            processing_queue: Queue,
            normalizer: DataNormalizer,
            alert_manager: AlertManager
    ):
        """
        Inicializa el servicio base.

        Args:
            input_queue (Queue): Cola de donde este servicio leerá datos crudos.
            processing_queue (Queue): Cola donde este servicio pondrá datos
                                      normalizados para el Orchestrator.
            normalizer (DataNormalizer): Instancia de un normalizador
                                         específico.
            alert_manager (AlertManager): Instancia para enviar alertas.
        """
        self.input_queue = input_queue
        self.processing_queue = processing_queue
        self.normalizer = normalizer
        self.alert_manager = alert_manager
        self._is_running = False
        self.metrics = MetricsCollector()  # <--- AÑADE ESTA LÍNEA

    @abstractmethod
    def _check_for_critical_events(self, data: Dict[str, Any]) -> bool:
        """
        Método abstracto para verificar si los datos contienen un evento crítico.
        Debe ser implementado por cada subclase.

        Args:
            data (Dict[str, Any]): Los datos normalizados.

        Returns:
            bool: True si es un evento crítico, False en caso contrario.
        """
        pass

    async def _process_data(self, raw_data: Any):
        """
        Lógica interna para procesar una única pieza de datos.
        """
        try:
            # 1. Normalizar y validar [cite: 12]
            normalized_data = self.normalizer.normalize(raw_data)

            self.metrics.record_event(normalized_data.get("type", "unknown"))

            # 2. Enviar alertas inmediatas si es crítico
            if self._check_for_critical_events(normalized_data):
                await self.alert_manager.send_alert(
                    level="CRITICAL",
                    message=f"Evento crítico detectado en {self.__class__.__name__}",
                    data=normalized_data
                )

            # 3. Enviar a la cola de procesamiento para análisis profundo
            # (El Orchestrator estará escuchando esta cola)
            await self.processing_queue.put(normalized_data)

        except ValueError as e:
            # Error de validación/normalización
            print(f"Error de validación en {self.__class__.__name__}: {e}")
            # Aquí se podría enviar a una cola de "datos fallidos"
        except Exception as e:
            print(f"Error inesperado procesando datos: {e}")

    async def start(self):
        """
        Inicia el "consumidor" de este servicio.
        Escucha continuamente la cola de entrada y procesa los datos.
        """
        self._is_running = True
        print(f"Iniciando {self.__class__.__name__}...")
        while self._is_running:
            try:
                # Espera por datos crudos en su cola de entrada
                raw_data = await self.input_queue.get()

                # Procesa los datos
                await self._process_data(raw_data)

                # Marca la tarea como completada en la cola
                self.input_queue.task_done()
            except asyncio.CancelledError:
                print(f"Deteniendo {self.__class__.__name__}...")
                self._is_running = False

    def stop(self):
        """
        Señal para detener el bucle de procesamiento.
        """
        self._is_running = False