
document.addEventListener("DOMContentLoaded", () => {

    const metricTotalProcessed = document.getElementById("metric-total-processed");
    const metricTotalErrors = document.getElementById("metric-total-errors");
    const metricAlertLatency = document.getElementById("metric-alert-latency");
    const alertList = document.getElementById("alert-list");

    const MAX_DATA_POINTS = 50;

    const lineCtx = document.getElementById('realTimeLatencyChart').getContext('2d');
    const realTimeLatencyChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Genetic',
                    data: [],
                    borderColor: '#e53935',
                    backgroundColor: 'rgba(229, 57, 53, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    spanGaps: true
                },
                {
                    label: 'Biochemical',
                    data: [],
                    borderColor: '#1e88e5',
                    backgroundColor: 'rgba(30, 136, 229, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    spanGaps: true
                },
                {
                    label: 'Physical',
                    data: [],
                    borderColor: '#43a047',
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
                    type: 'time',
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


    function addDataToChart(label, value) {
        const now = new Date();

        realTimeLatencyChart.data.labels.push(now);

        realTimeLatencyChart.data.datasets.forEach(dataset => {
            if (dataset.label.toLowerCase() === label.toLowerCase()) {
                dataset.data.push(value);
            } else {
                dataset.data.push(null);
            }
        });

        if (realTimeLatencyChart.data.labels.length > MAX_DATA_POINTS) {
            realTimeLatencyChart.data.labels.shift();
            realTimeLatencyChart.data.datasets.forEach(dataset => {
                dataset.data.shift();
            });
        }

        realTimeLatencyChart.update('none');
    }


    function addAlertToList(message, level) {
        const li = document.createElement("li");
        li.className = `alert-level-${level.toLowerCase()}`;
        li.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        alertList.prepend(li);
        while (alertList.children.length > 10) {
            alertList.removeChild(alertList.lastChild);
        }
    }


    function connectWebSocket() {
        const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${wsProtocol};

        console.log("Conectando a WebSocket en:", wsUrl);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => console.log("WebSocket conectado.");
        ws.onclose = () => {
            console.log("WebSocket desconectado. Intentando reconectar en 3s...");
            setTimeout(connectWebSocket, 3000);
        };
        ws.onerror = (error) => console.error("Error de WebSocket:", error);

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Mensaje WebSocket Recibido:", data);
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


    async function updateAggregateMetrics() {
        try {
            const response = await fetch('/api/metrics');
            if (!response.ok) return;
            const stats = await response.json();

            metricTotalProcessed.textContent = stats.events_processed.total;
            metricTotalErrors.textContent = stats.errors_count.total;
            metricAlertLatency.textContent = stats.average_alert_latency_ms.toFixed(2);

        } catch (error) {
            console.error("Error en updateAggregateMetrics:", error);
        }
    }

    connectWebSocket();

    updateAggregateMetrics();
    setInterval(updateAggregateMetrics, 2000);
});