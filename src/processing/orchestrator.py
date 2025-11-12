
import asyncio
import time
from asyncio import Queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Dict, Any

from . import io_tasks, cpu_tasks
from web.connection_manager import data_queue
from monitoring import MetricsCollector


class DataOrchestrator:

    def __init__(self, processing_queue: Queue, max_cpu_workers: int = 4):

        self.processing_queue = processing_queue

        self.cpu_executor = ProcessPoolExecutor(max_workers=max_cpu_workers)

        self.io_executor = ThreadPoolExecutor(max_workers=10)

        self._is_running = False
        self.metrics = MetricsCollector()

    async def _route_and_process_task(self, data: Dict[str, Any]):

        try:
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

                print(f"[Orchestrator] Enviando latencia bioquímica: {duration_ms:.2f} ms")  # <--- Log de depuración
                await data_queue.put({
                    "type": "latency",
                    "label": "Biochemical",
                    "value": duration_ms
                })

            elif data_type == "physical":
                print(f"[Orchestrator] Delegando Tarea I/O (Física): {data['subject_id']}")
                await loop.run_in_executor(
                    self.io_executor,
                    io_tasks.save_vitals_to_file_sync,
                    data
                )

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

            if result:
                await io_tasks.save_analysis_to_db_async(result)

        except Exception as e:
            print(f"[Orchestrator] Error fatal procesando tarea: {e} | Data: {data}")

    async def start(self):

        self._is_running = True
        print("[Orchestrator] Iniciado. Esperando datos...")
        while self._is_running:
            try:
                data = await self.processing_queue.get()

                asyncio.create_task(self._route_and_process_task(data))

                self.processing_queue.task_done()

            except asyncio.CancelledError:
                self._is_running = False

        print("[Orchestrator] Deteniendo...")
        await self.shutdown()

    async def shutdown(self):

        print("[Orchestrator] Apagando pools de ejecutores...")
        self.io_executor.shutdown(wait=True)
        self.cpu_executor.shutdown(wait=True)
        print("[Orchestrator] Apagado completo.")