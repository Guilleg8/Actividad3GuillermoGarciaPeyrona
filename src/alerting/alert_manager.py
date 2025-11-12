
import asyncio
import time
from typing import Dict, Any

from monitoring import MetricsCollector
from web.connection_manager import data_queue


class AlertManager:

    def __init__(self):

        self.metrics = MetricsCollector()
        self.alert_cooldowns = {}
        self.cooldown_period_sec = 60

    async def send_alert(self, level: str, message: str, data: Dict[str, Any]):

        alert_key_parts = [message]
        if "sample_id" in data:
            alert_key_parts.append(data["sample_id"])
        elif "subject_id" in data:
            alert_key_parts.append(data["subject_id"])

        alert_key = tuple(alert_key_parts)

        now = time.monotonic()
        last_alert_time = self.alert_cooldowns.get(alert_key, 0)

        if (now - last_alert_time) < self.cooldown_period_sec:
            return

        self.alert_cooldowns[alert_key] = now

        start_time = time.perf_counter()

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
            await asyncio.sleep(0.1)


        except Exception as e:
            print(f"    [AlertManager] ERROR al enviar alerta: {e}")
            self.metrics.record_error("alerting")

        finally:
            self.metrics.record_alert_latency(start_time)