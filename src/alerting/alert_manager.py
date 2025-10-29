# src/umbrella_analysis/alerting/alert_manager.py

import asyncio
import time
from typing import Dict, Any

# Importamos el singleton de métricas
from monitoring import MetricsCollector
from web.connection_manager import data_queue


class AlertManager:
    """
    Gestiona el envío de alertas críticas en tiempo real.

    Esta clase es instanciada y pasada a los servicios.
    Sus métodos son asíncronos para no bloquear el procesamiento
    de datos durante el envío de alertas.
    """

    def __init__(self):
        """
        Inicializa el AlertManager.

        Obtiene la instancia única del MetricsCollector para poder
        registrar la latencia de las alertas.
        """
        self.metrics = MetricsCollector()
        self.alert_cooldowns = {}  # Para evitar spam de alertas
        self.cooldown_period_sec = 60  # 1 minuto

    async def send_alert(self, level: str, message: str, data: Dict[str, Any]):
        """
        Procesa y envía una alerta al sistema externo.

        Registra la latencia de esta operación.

        Args:
            level (str): Nivel de criticidad (ej. "CRITICAL", "WARNING").
            message (str): Mensaje de la alerta.
            data (Dict[str, Any]): Datos que dispararon la alerta.
        """

        # Clave simple para anti-spam (basada en el mensaje y el ID)
        alert_key_parts = [message]
        if "sample_id" in data:
            alert_key_parts.append(data["sample_id"])
        elif "subject_id" in data:
            alert_key_parts.append(data["subject_id"])

        alert_key = tuple(alert_key_parts)

        # --- Lógica de Anti-Spam (Cooldown) ---
        now = time.monotonic()
        last_alert_time = self.alert_cooldowns.get(alert_key, 0)

        if (now - last_alert_time) < self.cooldown_period_sec:
            # Aún en período de cooldown, ignorar alerta
            # print(f"[AlertManager] Alerta duplicada suprimida (cooldown): {message}")
            return

        # No está en cooldown, registrar esta alerta y continuar
        self.alert_cooldowns[alert_key] = now
        # ----------------------------------------

        start_time = time.perf_counter()

        # Formateo del mensaje
        alert_log = f"🚨 ALERTA [{level.upper()}] 🚨: {message}"
        if "sample_id" in data:
            alert_log += f" | Sample: {data['sample_id']}"
        if "subject_id" in data:
            alert_log += f" | Subject: {data['subject_id']}"

        print(alert_log)

        try:
            await data_queue.put({
                "type": "alert",
                "level": level.upper(),
                "message": message
            })
            await asyncio.sleep(0.1)  # Simula 100ms de latencia de red


        except Exception as e:
            print(f"    [AlertManager] ERROR al enviar alerta: {e}")
            self.metrics.record_error("alerting")

        finally:
            # Registra la latencia de la alerta
            # (El tiempo desde que se llama a este método hasta que termina)
            self.metrics.record_alert_latency(start_time)