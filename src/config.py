# src/umbrella_analysis/config.py

"""
Archivo de Configuración Centralizado

Contiene las variables de configuración para el sistema de análisis.
"""

# --- Configuración de Concurrencia ---

# Número de procesos worker para el ProcessPoolExecutor.
# AJUSTAR ESTO basado en el número de núcleos de CPU de tu máquina.
# Un buen punto de partida es (Nº de CPUs - 1)
MAX_CPU_WORKERS: int = 4

# Número máximo de hilos para el ThreadPoolExecutor (tareas de E/S bloqueante)
MAX_IO_WORKERS: int = 10


# --- Configuración de Simulación ---

# Factor de velocidad para los 'data_fetchers' de ingestión.
# 1.0 = Velocidad normal
# 2.0 = Doble de velocidad
# 0.5 = Mitad de velocidad
SIMULATION_SPEED: float = 1.0