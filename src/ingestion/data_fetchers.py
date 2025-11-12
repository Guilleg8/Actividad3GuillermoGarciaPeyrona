
import asyncio
import random
import uuid
from asyncio import Queue


async def simulate_genetic_data_feed(queue: Queue, simulation_speed: float = 1.0):

    print("[Ingestion] Iniciando feed de datos genéticos...")
    while True:
        await asyncio.sleep(random.uniform(0.5, 2.0) / simulation_speed)

        raw_sequence = "ATCG" * random.randint(5, 10)
        if random.random() < 0.1:
            pos = random.randint(0, len(raw_sequence) - 1)
            raw_sequence = raw_sequence[:pos] + "T" + raw_sequence[pos + 1:]
        elif random.random() < 0.05:
            pos = random.randint(0, len(raw_sequence) - 1)
            raw_sequence = raw_sequence[:pos] + "G" + raw_sequence[pos + 1:]

        data = {
            "sample_id": str(uuid.uuid4()),
            "raw_sequence": raw_sequence,
            "metadata": {"source_lab": "Lab-01"}
        }

        await queue.put(data)


async def simulate_biochemical_data_feed(queue: Queue, simulation_speed: float = 1.0):

    print("[Ingestion] Iniciando feed de datos bioquímicos...")
    while True:
        await asyncio.sleep(random.uniform(0.2, 1.0) / simulation_speed)

        if random.random() < 0.1:
            toxin = f"{random.uniform(80.1, 95.0):.2f} ppm"
        else:
            toxin = f"{random.uniform(10.0, 50.0):.2f} ppm"

        data = {
            "sample_id": f"bio_{random.randint(1000, 9999)}",
            "toxin_level": toxin,
            "protein_x": random.uniform(1.0, 15.0)
        }

        await queue.put(data)


async def simulate_physical_data_feed(queue: Queue, simulation_speed: float = 1.0):

    print("[Ingestion] Iniciando feed de datos físicos...")
    while True:
        await asyncio.sleep(random.uniform(1.0, 3.0) / simulation_speed)

        heart_rate = random.randint(55, 100)
        spo2 = f"{random.randint(95, 99)}%"

        rand_event = random.random()
        if rand_event < 0.05:
            heart_rate = 0
        elif rand_event < 0.1:
            heart_rate = random.randint(191, 220)
        elif rand_event < 0.15:
            spo2 = f"{random.randint(80, 89)}%"

        data = {
            "subject_id": f"subject_{random.randint(1, 10)}",
            "vitals": {
                "heart_rate": heart_rate,
                "spo2": spo2
            }
        }

        await queue.put(data)
