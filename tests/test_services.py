# tests/test_processing.py

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Componentes a probar
from src.processing import DataOrchestrator
from src.processing import cpu_tasks
from src.processing import io_tasks


# --- Pruebas para las tareas (Tasks) ---

def test_cpu_task_analyze_genetic_sequence():
    """Prueba la lógica pura de la tarea CPU-bound genética."""
    # Desactivamos la simulación de cómputo para que el test sea instantáneo
    cpu_tasks._simulate_heavy_computation = MagicMock()

    data = {"sample_id": "g-test", "sequence": "ATCGT"}
    result = cpu_tasks.analyze_genetic_sequence(data)

    assert result["analysis_id"] == "res_g-test"
    assert result["finding"] == "Mutación T-Virus detectada"
    assert result["analysis_type"] == "genetic"


def test_cpu_task_analyze_biochemical_model():
    """Prueba la lógica pura de la tarea CPU-bound bioquímica."""
    cpu_tasks._simulate_heavy_computation = MagicMock()

    data = {"sample_id": "b-test"}
    result = cpu_tasks.analyze_biochemical_model(data)

    assert result["analysis_id"] == "res_b-test"
    assert result["finding"] == "Niveles de toxina inestables"
    assert result["analysis_type"] == "biochemical"


@pytest.mark.asyncio
async def test_io_task_save_analysis_to_db_async(mocker):
    """Prueba la tarea I/O asíncrona (simulando sleep)."""
    # Simulamos asyncio.sleep para que no tarde
    mocker.patch("asyncio.sleep", new_callable=AsyncMock)

    data = {"analysis_id": "io-async-test"}
    # La prueba simplemente verifica que se puede ejecutar sin errores
    await io_tasks.save_analysis_to_db_async(data)
    asyncio.sleep.assert_called_once_with(0.5)  # Verifica que se llamó al sleep


def test_io_task_save_vitals_to_file_sync(mocker):
    """Prueba la tarea I/O síncrona (simulando sleep)."""
    # Simulamos time.sleep para que no tarde
    mocker.patch("time.sleep")

    data = {"subject_id": "io-sync-test"}
    # La prueba simplemente verifica que se puede ejecutar sin errores
    io_tasks.save_vitals_to_file_sync(data)
    time.sleep.assert_called_once_with(0.2)  # Verifica que se llamó al sleep


# --- Pruebas para el Orchestrator ---

@pytest.fixture
def mock_orchestrator(mocker):
    """Fixture que crea un Orchestrator con ejecutores y colas simulados."""
    orchestrator = DataOrchestrator(
        processing_queue=AsyncMock(spec=asyncio.Queue),
        max_cpu_workers=1
    )

    # Simular (mock) los ejecutores para que no creen procesos/hilos reales
    orchestrator.cpu_executor = MagicMock()
    orchestrator.io_executor = MagicMock()

    # Simular el bucle de eventos de asyncio
    mock_loop = MagicMock()
    # Hacemos que loop.run_in_executor sea un AsyncMock para poder 'await'
    mock_loop.run_in_executor = AsyncMock()
    mocker.patch("asyncio.get_running_loop", return_value=mock_loop)

    return orchestrator, mock_loop


@pytest.mark.asyncio
async def test_orchestrator_routes_genetic_task(mock_orchestrator, mocker):
    """Prueba que los datos 'genetic' se enrutan al pool de CPU."""
    orchestrator, mock_loop = mock_orchestrator

    # Simular que el guardado en BBDD también funciona
    mocker.patch("umbrella_analysis.processing.io_tasks.save_analysis_to_db_async",
                 new_callable=AsyncMock)

    data = {"sample_id": "g-route-test", "type": "genetic"}

    await orchestrator._route_and_process_task(data)

    # Verificación clave:
    # ¿Se llamó a run_in_executor con el POOL DE CPU
    # y la TAREA DE CPU correcta?
    mock_loop.run_in_executor.assert_called_once_with(
        orchestrator.cpu_executor,
        cpu_tasks.analyze_genetic_sequence,
        data
    )

    # Verificar que el resultado se envió a guardar
    io_tasks.save_analysis_to_db_async.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_routes_physical_task(mock_orchestrator, mocker):
    """Prueba que los datos 'physical' se enrutan al pool de I/O."""
    orchestrator, mock_loop = mock_orchestrator

    # Simular la tarea de guardado en BBDD (no debería llamarse)
    mocker.patch("umbrella_analysis.processing.io_tasks.save_analysis_to_db_async",
                 new_callable=AsyncMock)

    data = {"subject_id": "p-route-test", "type": "physical"}

    await orchestrator._route_and_process_task(data)

    # Verificación clave:
    # ¿Se llamó a run_in_executor con el POOL DE I/O
    # y la TAREA DE I/O correcta?
    mock_loop.run_in_executor.assert_called_once_with(
        orchestrator.io_executor,
        io_tasks.save_vitals_to_file_sync,
        data
    )

    # Verificar que el resultado NO se envió a guardar (la tarea física no retorna)
    io_tasks.save_analysis_to_db_async.assert_not_called()


@pytest.mark.asyncio
async def test_orchestrator_routes_unknown_task(mock_orchestrator):
    """Prueba que los datos desconocidos se manejan sin fallar."""
    orchestrator, mock_loop = mock_orchestrator

    data = {"id": "unknown-test", "type": "unknown"}

    # Simplemente ejecuta para asegurar que no lanza una excepción
    await orchestrator._route_and_process_task(data)

    # No se debe llamar a ningún ejecutor
    mock_loop.run_in_executor.assert_not_called()