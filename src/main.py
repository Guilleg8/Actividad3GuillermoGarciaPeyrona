import asyncio


from src import config

from communication import (
    genetic_input_queue,
    biochemical_input_queue,
    physical_input_queue,
    processing_queue,
)

from ingestion import (
    simulate_genetic_data_feed,
    simulate_biochemical_data_feed,
    simulate_physical_data_feed
)

from normalization import (
    GeneticNormalizer,
    BiochemicalNormalizer,
    PhysicalNormalizer
)

from services import (
    GeneticoService,
    BioquimicoService,
    FisicoService
)

from alerting import AlertManager

from processing import DataOrchestrator


async def main():

    print("--- Iniciando Sistema de Análisis de Umbrella Corporation ---")

    tasks = []

    try:

        alert_manager = AlertManager()

        genetic_norm = GeneticNormalizer()
        biochem_norm = BiochemicalNormalizer()
        physical_norm = PhysicalNormalizer()

        genetico_service = GeneticoService(
            input_queue=genetic_input_queue,
            processing_queue=processing_queue,
            normalizer=genetic_norm,
            alert_manager=alert_manager
        )

        bioquimico_service = BioquimicoService(
            input_queue=biochemical_input_queue,
            processing_queue=processing_queue,
            normalizer=biochem_norm,
            alert_manager=alert_manager
        )

        fisico_service = FisicoService(
            input_queue=physical_input_queue,
            processing_queue=processing_queue,
            normalizer=physical_norm,
            alert_manager=alert_manager
        )

        orchestrator = DataOrchestrator(
            processing_queue=processing_queue,
            max_cpu_workers=config.MAX_CPU_WORKERS
        )

        tasks.append(asyncio.create_task(
            simulate_genetic_data_feed(genetic_input_queue, config.SIMULATION_SPEED)
        ))
        tasks.append(asyncio.create_task(
            simulate_biochemical_data_feed(biochemical_input_queue, config.SIMULATION_SPEED)
        ))
        tasks.append(asyncio.create_task(
            simulate_physical_data_feed(physical_input_queue, config.SIMULATION_SPEED)
        ))

        tasks.append(asyncio.create_task(genetico_service.start()))
        tasks.append(asyncio.create_task(bioquimico_service.start()))
        tasks.append(asyncio.create_task(fisico_service.start()))

        orchestrator_task = asyncio.create_task(orchestrator.start())

        print(f"Sistema en marcha. {len(tasks)} tareas de fondo + orquestador.")
        print("Presiona Ctrl+C para detener.")

        await orchestrator_task

    except asyncio.CancelledError:
        print("\n[Main] Solicitud de apagado recibida.")

    finally:
        print("[Main] Iniciando apagado ordenado...")

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        if 'orchestrator' in locals():
            await orchestrator.shutdown()

        print("--- Sistema de Análisis Detenido ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Main] Apagado forzado por el usuario.")