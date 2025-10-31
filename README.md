# Sistema de Análisis Concurrente de Umbrella

Este proyecto es una simulación de un sistema de análisis de datos biológicos en tiempo real, desarrollado como solución a la "Actividad 3 - Programación concurrente".

El sistema ingiere flujos de datos heterogéneos (Genéticos, Bioquímicos y Físicos), los procesa concurrentemente utilizando un modelo híbrido de `asyncio` y multiprocesamiento, y visualiza los resultados en un dashboard web en tiempo real.

## 1. Arquitectura y Tecnologías

El proyecto se divide en un backend de procesamiento y un frontend de visualización.

### Backend
* **Lenguaje:** Python 3.11+
* **Framework Web:** FastAPI
* **Concurrencia:**
    * **`asyncio`**: Para gestionar las E/S de red (WebSockets) y la orquestación general de tareas.
    * **`concurrent.futures.ProcessPoolExecutor`**: Para tareas intensivas en CPU (análisis genético/bioquímico), evitando bloquear el bucle de eventos.
    * **`concurrent.futures.ThreadPoolExecutor`**: Para tareas de E/S bloqueantes (simulación de escritura en disco).
* **Comunicación en vivo:** WebSockets (vía FastAPI).
* **Validación de Datos:** Pydantic.

### Frontend
* **HTML5 / CSS3**
* **JavaScript (ES6+)**
* **Gráficos:** Chart.js (servido localmente).

---

## 2. Flujo de Datos

El sistema sigue un patrón de Productor-Consumidor en varias etapas:

1.  **Ingesta (`ingestion/`):** Tres simuladores `async` actúan como productores, generando datos y metiéndolos en tres colas de entrada distintas (`genetic_input_queue`, `biochemical_input_queue`, `physical_input_queue`).
2.  **Servicios (`services/`):** Cada clase de servicio (ej. `GeneticoService`) actúa como consumidor de su cola de entrada.
    * **Normaliza** los datos usando Pydantic.
    * **Alerta** si detecta una anomalía (ej. "T-VIRUS").
    * **Registra** la métrica en `MetricsCollector`.
    * Actúa como productor para la siguiente etapa, poniendo los datos limpios en la `processing_queue`.
3.  **Orquestador (`processing/`):** `DataOrchestrator` es el consumidor final.
    * Toma datos de la `processing_queue`.
    * Delega el trabajo pesado a los *pools* de procesos/hilos.
4.  **Difusión (`web/`):** El Orquestador y el AlertManager envían los resultados (latencia, alertas) a la `data_queue`.
5.  **Visualización:** El `websocket_broadcaster` envía estos mensajes a `dashboard.js`, que actualiza el gráfico de Chart.js.

---

## 3. Estructura del Proyecto

El código fuente está contenido íntegramente en la carpeta `src/`.

src/ ├── alerting/ # Gestiona el envío de alertas (AlertManager) ├── communication/ # Define las colas (asyncio.Queue) que conectan los módulos ├── ingestion/ # Simula la entrada de datos (Data Fetchers) ├── monitoring/ # Colector de métricas Singleton (MetricsCollector) ├── normalization/ # Clases de validación y limpieza de datos (Pydantic) ├── processing/ # Lógica de concurrencia pesada (DataOrchestrator, Tareas CPU/IO) ├── services/ # Lógica de negocio de primer nivel (GeneticoService, etc.) ├── web/ # Servidor web FastAPI y frontend │ ├── static/ # Archivos CSS y JS (incluyendo Chart.js) │ └── templates/ # Archivo index.html ├── config.py # Archivo de configuración (ej. MAX_CPU_WORKERS) └── main.py # Punto de entrada del backend (ensambla los servicios)


---

## 4. Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone [URL-DEL-REPOSITORIO]
    cd Actividad3GuillermoGarciaPeyrona
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    
    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    (Asegúrate de tener un archivo `requirements.txt` en la raíz del proyecto).
    ```bash
    pip install -r requirements.txt
    ```

---

## 5. Ejecución

Para iniciar el sistema (backend y frontend), ejecuta el script `run.py` desde la raíz del proyecto:

```bash
python run.py
