# src/umbrella_analysis/ingestion/data_fetchers.py

import asyncio
import random
import uuid
from asyncio import Queue


async def simulate_genetic_data_feed(queue: Queue, simulation_speed: float = 1.0):
    """
    Simula un flujo de datos genéticos (ej. secuenciador de ADN).

    Args:
        queue (Queue): La cola de asyncio donde se pondrán los datos.
        simulation_speed (float): Factor de velocidad (1.0 = normal).
    """
    print("[Ingestion] Iniciando feed de datos genéticos...")
    while True:
        # Simula tiempo de llegada aleatorio
        await asyncio.sleep(random.uniform(0.5, 2.0) / simulation_speed)

        # Genera datos crudos (aún no normalizados)
        raw_sequence = "ATCG" * random.randint(5, 10)
        # Introduce mutaciones aleatorias, incluyendo las críticas
        if random.random() < 0.1:  # 10% de probabilidad de T-Virus
            pos = random.randint(0, len(raw_sequence) - 1)
            raw_sequence = raw_sequence[:pos] + "T" + raw_sequence[pos + 1:]
        elif random.random() < 0.05:  # 5% de probabilidad de G-Virus
            pos = random.randint(0, len(raw_sequence) - 1)
            raw_sequence = raw_sequence[:pos] + "G" + raw_sequence[pos + 1:]

        data = {
            "sample_id": str(uuid.uuid4()),
            "raw_sequence": raw_sequence,
            "metadata": {"source_lab": "Lab-01"}
        }

        await queue.put(data)
        # print(f"[Ingestor Genético] Nuevo dato: {data['sample_id']}")


async def simulate_biochemical_data_feed(queue: Queue, simulation_speed: float = 1.0):
    """
    Simula un flujo de datos bioquímicos (ej. analizador de sangre).

    Args:
        queue (Queue): La cola de asyncio donde se pondrán los datos.
        simulation_speed (float): Factor de velocidad (1.0 = normal).
    """
    print("[Ingestion] Iniciando feed de datos bioquímicos...")
    while True:
        await asyncio.sleep(random.uniform(0.2, 1.0) / simulation_speed)

        # Genera datos crudos (con formatos sucios para el normalizador)
        if random.random() < 0.1:  # 10% de probabilidad de evento crítico
            toxin = f"{random.uniform(80.1, 95.0):.2f} ppm"
        else:
            toxin = f"{random.uniform(10.0, 50.0):.2f} ppm"

        data = {
            "sample_id": f"bio_{random.randint(1000, 9999)}",
            "toxin_level": toxin,  # Nótese que es un string
            "protein_x": random.uniform(1.0, 15.0)  # protein_x_level
        }

        await queue.put(data)
        # print(f"[Ingestor Bioquímico] Nuevo dato: {data['sample_id']}")


async def simulate_physical_data_feed(queue: Queue, simulation_speed: float = 1.0):
    """
    Simula un flujo de datos físicos (ej. monitor de signos vitales).

    Args:
        queue (Queue): La cola de asyncio donde se pondrán los datos.
        simulation_speed (float): Factor de velocidad (1.0 = normal).
    """
    print("[Ingestion] Iniciando feed de datos físicos...")
    while True:
        await asyncio.sleep(random.uniform(1.0, 3.0) / simulation_speed)

        heart_rate = random.randint(55, 100)
        spo2 = f"{random.randint(95, 99)}%"  # Formato string

        # Simula eventos críticos
        rand_event = random.random()
        if rand_event < 0.05:  # Paro cardíaco
            heart_rate = 0
        elif rand_event < 0.1:  # Taquicardia
            heart_rate = random.randint(191, 220)
        elif rand_event < 0.15:  # Hipoxia
            spo2 = f"{random.randint(80, 89)}%"

        data = {
            "subject_id": f"subject_{random.randint(1, 10)}",
            "vitals": {
                "heart_rate": heart_rate,
                "spo2": spo2
            }
        }

        await queue.put(data)
        # print(f"[Ingestor Físico] Nuevo dato: {data['subject_id']}")