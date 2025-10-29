// src/umbrella_analysis/web/static/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {

    // --- Referencias a elementos del DOM ---
    const metricTotalProcessed = document.getElementById("metric-total-processed");
    const metricTotalErrors = document.getElementById("metric-total-errors");
    const metricAlertLatency = document.getElementById("metric-alert-latency");
    const alertList = document.getElementById("alert-list");

    // --- Configuración del Gráfico de Línea ---
    const MAX_DATA_POINTS = 50; // ¿Cuántos puntos mostrar antes de que se "deslice"?

    const lineCtx = document.getElementById('realTimeLatencyChart').getContext('2d');
    const realTimeLatencyChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            // Los 'labels' serán las marcas de tiempo
            labels: [],
            datasets: [
                {
                    label: 'Genetic',
                    data: [],
                    borderColor: '#e53935', // Rojo
                    backgroundColor: 'rgba(229, 57, 53, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    spanGaps: true
                },
                {
                    label: 'Biochemical',
                    data: [],
                    borderColor: '#1e88e5', // Azul
                    backgroundColor: 'rgba(30, 136, 229, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    spanGaps: true
                },
                {
                    label: 'Physical',
                    data: [],
                    borderColor: '#43a047', // Verde
                    backgroundColor: 'rgba(67, 160, 71, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Latencia (ms)', color: '#e0e0e0' },
                    ticks: { color: '#e0e0e0' },
                    grid: { color: '#444' }
                },
                x: {
                    type: 'time', // Usamos una escala de tiempo
                    time: { unit: 'second', displayFormats: { second: 'HH:mm:ss' } },
                    ticks: { color: '#e0e0e0' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { position: 'top', labels: { color: '#e0e0e0' } }
            }
        }
    });

    /**
     * Añade datos al gráfico de línea de forma deslizante.
     */
    function addDataToChart(label, value) {
        const now = new Date();

        // Añade la marca de tiempo a los labels
        realTimeLatencyChart.data.labels.push(now);

        // Añade el dato al dataset correcto (y 'null' a los otros)
        realTimeLatencyChart.data.datasets.forEach(dataset => {
            if (dataset.label.toLowerCase() === label.toLowerCase()) {
                dataset.data.push(value);
            } else {
                dataset.data.push(null); // 'null' crea un hueco en el gráfico
            }
        });

        // Elimina datos viejos si se supera el límite
        if (realTimeLatencyChart.data.labels.length > MAX_DATA_POINTS) {
            realTimeLatencyChart.data.labels.shift(); // Quita el label más viejo
            realTimeLatencyChart.data.datasets.forEach(dataset => {
                dataset.data.shift(); // Quita el dato más viejo
            });
        }

        realTimeLatencyChart.update('none'); // 'none' para una actualización sin animación
    }

    /**
     * Añade una alerta a la lista de alertas.
     */
    function addAlertToList(message, level) {
        const li = document.createElement("li");
        li.className = `alert-level-${level.toLowerCase()}`;
        li.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        // Añade al principio de la lista
        alertList.prepend(li);
        // Limita la lista
        while (alertList.children.length > 10) {
            alertList.removeChild(alertList.lastChild);
        }
    }

    // --- Conexión WebSocket ---

    function connectWebSocket() {
        // Asegura que la URL es correcta (ws:// en lugar de http://)
        const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

        console.log("Conectando a WebSocket en:", wsUrl);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => console.log("WebSocket conectado.");
        ws.onclose = () => {
            console.log("WebSocket desconectado. Intentando reconectar en 3s...");
            setTimeout(connectWebSocket, 3000); // Intenta reconectar
        };
        ws.onerror = (error) => console.error("Error de WebSocket:", error);

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Mensaje WebSocket Recibido:", data);
                // Enruta el evento recibido
                switch(data.type) {
                    case "latency":
                        addDataToChart(data.label, data.value);
                        break;
                    case "alert":
                        addAlertToList(data.message, data.level);
                        break;
                }
            } catch (e) {
                console.error("Error procesando mensaje de WS:", e);
            }
        };
    }

    // --- Conexión Fetch (para los totales) ---

    async function updateAggregateMetrics() {
        try {
            const response = await fetch('/api/metrics');
            if (!response.ok) return;
            const stats = await response.json();

            // Actualiza las tarjetas (cards)
            metricTotalProcessed.textContent = stats.events_processed.total;
            metricTotalErrors.textContent = stats.errors_count.total;
            metricAlertLatency.textContent = stats.average_alert_latency_ms.toFixed(2);

        } catch (error) {
            console.error("Error en updateAggregateMetrics:", error);
        }
    }

    // --- Inicio ---
    connectWebSocket(); // Inicia la conexión en vivo

    // Sigue pidiendo los totales (agregados) cada 2 segundos
    updateAggregateMetrics();
    setInterval(updateAggregateMetrics, 2000);
});