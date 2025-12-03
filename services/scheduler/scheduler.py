import asyncio
import logging
import os

from dotenv import load_dotenv
from prometheus_client import Counter, Gauge, start_http_server

from .tasks import SchedulerTasks


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class SchedulerService:
    def __init__(self, interval_seconds: int | None = None):
        load_dotenv()
        self.interval = interval_seconds or int(
            os.getenv("SCHEDULER_INTERVAL_SECONDS", "300")
        )
        self.tasks = SchedulerTasks()
        self.cycles_counter = Counter(
            "scheduler_cycles_total", "Scheduler cycles completed"
        )
        self.targets_gauge = Gauge(
            "scheduler_last_targets_count",
            "Number of targets enqueued in last cycle",
        )

    async def run_once(self) -> int:
        """Trigger a single scheduling cycle."""
        count = await asyncio.to_thread(self.tasks.enqueue_targets)
        logger.info("Scheduler cycle complete: %s targets", count)
        self.cycles_counter.inc()
        self.targets_gauge.set(count)
        return count

    async def run(self):
        logger.info("Scheduler service starting (interval=%ss)", self.interval)
        while True:
            try:
                await self.run_once()
            except Exception as exc:
                logger.exception("Scheduler cycle failed: %s", exc)
            await asyncio.sleep(self.interval)


if __name__ == "__main__":
    service = SchedulerService()
    start_http_server(int(os.getenv("SCHEDULER_METRICS_PORT", "8002")))
    asyncio.run(service.run())