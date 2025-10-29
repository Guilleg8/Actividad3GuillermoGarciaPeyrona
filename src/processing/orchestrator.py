# src/umbrella_analysis/processing/orchestrator.py

import asyncio
import time
from asyncio import Queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Dict, Any

from . import io_tasks, cpu_tasks
from web.connection_manager import data_queue
from monitoring import MetricsCollector


class DataOrchestrator:
    """
    Orquesta el procesamiento de datos concurrente.

    Utiliza asyncio como bucle principal para manejar tareas de E/S
    y delega tareas pesadas de CPU a un ProcessPoolExecutor.
    También gestiona un ThreadPoolExecutor para E/S bloqueante.
    """

    def __init__(self, processing_queue: Queue, max_cpu_workers: int = 4):
        """
        Inicializa el orquestador.

        Args:
            processing_queue (Queue): La cola de asyncio de donde se leen
                                      los datos normalizados por los servicios.
            max_cpu_workers (int): Número máximo de procesos para el pool de CPU.
        """
        self.processing_queue = processing_queue

        # Pool para tareas CPU-bound (cálculo pesado) [cite: 25]
        # Usamos ProcessPoolExecutor para escapar del GIL
        self.cpu_executor = ProcessPoolExecutor(max_workers=max_cpu_workers)

        # Pool para tareas I/O-bound bloqueantes (ej. escribir a disco) [cite: 26]
        self.io_executor = ThreadPoolExecutor(max_workers=10)

        self._is_running = False
        self.metrics = MetricsCollector()

    async def _route_and_process_task(self, data: Dict[str, Any]):
        """
        Enruta una tarea de datos al ejecutor apropiado basado en su tipo.
        """
        try:
            # Asumimos que el servicio añadió un 'type' al normalizar
            data_type = data.get("type", "unknown")
            loop = asyncio.get_running_loop()

            result = None
            start_time = time.perf_counter()

            if data_type == "genetic":
                result = await loop.run_in_executor(
                    self.cpu_executor,
                    cpu_tasks.analyze_genetic_sequence,
                    data
                )
                duration_ms = (time.perf_counter() - start_time) * 1000
                self.metrics.record_processing_time("genetic", duration_ms)

                # --- ¡VERIFICA QUE ESTE BLOQUE EXISTE! ---
                print(f"[Orchestrator] Enviando latencia genética: {duration_ms:.2f} ms")  # <--- Log de depuración
                await data_queue.put({
                    "type": "latency",
                    "label": "Genetic",
                    "value": duration_ms
                })

            elif data_type == "biochemical":
                result = await loop.run_in_executor(
                    self.cpu_executor,
                    cpu_tasks.analyze_biochemical_model,
                    data
                )
                duration_ms = (time.perf_counter() - start_time) * 1000
                self.metrics.record_processing_time("biochemical", duration_ms)

                # --- ¡VERIFICA QUE ESTE BLOQUE EXISTE! ---
                print(f"[Orchestrator] Enviando latencia bioquímica: {duration_ms:.2f} ms")  # <--- Log de depuración
                await data_queue.put({
                    "type": "latency",
                    "label": "Biochemical",
                    "value": duration_ms
                })

            elif data_type == "physical":
                # I/O-Bound: Guardar signos vitales (ej. I/O bloqueante)
                print(f"[Orchestrator] Delegando Tarea I/O (Física): {data['subject_id']}")
                await loop.run_in_executor(
                    self.io_executor,
                    io_tasks.save_vitals_to_file_sync,
                    data
                )

                # --- ¡AÑADE ESTO! ---
                duration_ms = (time.perf_counter() - start_time) * 1000
                self.metrics.record_processing_time("physical", duration_ms)

                print(f"[Orchestrator] Enviando latencia física: {duration_ms:.2f} ms")
                await data_queue.put({
                    "type": "latency",
                    "label": "Physical",
                    "value": duration_ms
                })
                # ---------------------
                return  #

            else:
                print(f"[Orchestrator] ERROR: Tipo de dato desconocido: {data_type}")
                return

            # Si la tarea CPU-bound generó un resultado, lo guardamos
            if result:
                await io_tasks.save_analysis_to_db_async(result)

        except Exception as e:
            print(f"[Orchestrator] Error fatal procesando tarea: {e} | Data: {data}")

    async def start(self):
        """
        Inicia el bucle principal del orquestador.
        Consume de la cola de procesamiento y crea tareas para procesar los datos.
        """
        self._is_running = True
        print("[Orchestrator] Iniciado. Esperando datos...")
        while self._is_running:
            try:
                # 1. Espera por datos normalizados de los servicios
                data = await self.processing_queue.get()

                # 2. Crea una nueva tarea de asyncio para manejar este dato
                #    Esto permite al bucle 'start' volver a esperar en .get()
                #    inmediatamente, logrando alta concurrencia.
                asyncio.create_task(self._route_and_process_task(data))

                # 3. Marca la tarea de la cola como completada
                self.processing_queue.task_done()

            except asyncio.CancelledError:
                self._is_running = False

        print("[Orchestrator] Deteniendo...")
        await self.shutdown()

    async def shutdown(self):
        """
        Detiene los pools de ejecutores de forma limpia.
        """
        print("[Orchestrator] Apagando pools de ejecutores...")
        self.io_executor.shutdown(wait=True)
        self.cpu_executor.shutdown(wait=True)
        print("[Orchestrator] Apagado completo.")