
import asyncio



genetic_input_queue = asyncio.Queue(maxsize=100)

biochemical_input_queue = asyncio.Queue(maxsize=100)

physical_input_queue = asyncio.Queue(maxsize=100)



processing_queue = asyncio.Queue(maxsize=300)
