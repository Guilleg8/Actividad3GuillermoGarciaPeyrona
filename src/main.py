# src/umbrella_analysis/main.py

import asyncio

# --- 1. Importar Configuración y Componentes ---

from src import config

# Importar colas y eventos
from communication import (
    genetic_input_queue,
    biochemical_input_queue,
    physical_input_queue,
    processing_queue,
)

# Importar simuladores de ingesta
from ingestion import (
    simulate_genetic_data_feed,
    simulate_biochemical_data_feed,
    simulate_physical_data_feed
)

# Importar normalizadores
from normalization import (
    GeneticNormalizer,
    BiochemicalNormalizer,
    PhysicalNormalizer
)

# Importar servicios
from services import (
    GeneticoService,
    BioquimicoService,
    FisicoService
)

# Importar gestor de alertas
from alerting import AlertManager

# Importar orquestador
from processing import DataOrchestrator


async def main():
    """
    Función principal de asyncio.
    Instancia todos los componentes y los inicia.
    """
    print("--- Iniciando Sistema de Análisis de Umbrella Corporation ---")

    # Lista para rastrear todas las tareas en segundo plano
    tasks = []

    try:
        # --- 2. Instanciación de Componentes ---

        # Componentes "Singleton"
        alert_manager = AlertManager()

        # Normalizadores
        genetic_norm = GeneticNormalizer()
        biochem_norm = BiochemicalNormalizer()
        physical_norm = PhysicalNormalizer()

        # Servicios (Inyección de Dependencias)
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

        # Orquestador
        orchestrator = DataOrchestrator(
            processing_queue=processing_queue,
            max_cpu_workers=config.MAX_CPU_WORKERS
        )

        # --- 3. Creación y Lanzamiento de Tareas ---

        # Tareas de Ingesta (Productores)
        tasks.append(asyncio.create_task(
            simulate_genetic_data_feed(genetic_input_queue, config.SIMULATION_SPEED)
        ))
        tasks.append(asyncio.create_task(
            simulate_biochemical_data_feed(biochemical_input_queue, config.SIMULATION_SPEED)
        ))
        tasks.append(asyncio.create_task(
            simulate_physical_data_feed(physical_input_queue, config.SIMULATION_SPEED)
        ))

        # Tareas de Servicio (Consumidores/Productores)
        tasks.append(asyncio.create_task(genetico_service.start()))
        tasks.append(asyncio.create_task(bioquimico_service.start()))
        tasks.append(asyncio.create_task(fisico_service.start()))

        # Tarea de Orquestador (Consumidor)
        # Se maneja por separado para un apagado limpio
        orchestrator_task = asyncio.create_task(orchestrator.start())

        print(f"Sistema en marcha. {len(tasks)} tareas de fondo + orquestador.")
        print("Presiona Ctrl+C para detener.")

        # Esperar a que el orquestador termine (o se cancele)
        await orchestrator_task

    except asyncio.CancelledError:
        print("\n[Main] Solicitud de apagado recibida.")

    finally:
        # --- 4. Lógica de Apagado Limpio ---
        print("[Main] Iniciando apagado ordenado...")

        # Señal a las tareas que usan el evento (si las hu
        # Cancelar todas las tareas de fondo (ingestores, servicios)
        for task in tasks:
            task.cancel()

        # Esperar a que todas las tareas se cancelen
        await asyncio.gather(*tasks, return_exceptions=True)

        # Apagar el orquestador (esto cierra los pools de procesos/hilos)
        if 'orchestrator' in locals():
            await orchestrator.shutdown()

        print("--- Sistema de Análisis Detenido ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Esto ocurre si Ctrl+C se presiona *antes* de que el
        # bucle de eventos esté manejando las CancelledError
        print("\n[Main] Apagado forzado por el usuario.")