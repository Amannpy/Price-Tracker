import asyncio
from unittest.mock import MagicMock

from services.scheduler.scheduler import SchedulerService


def test_scheduler_run_once_uses_tasks(monkeypatch):
    service = SchedulerService(interval_seconds=1)
    mock_tasks = MagicMock()
    mock_tasks.enqueue_targets.return_value = 5
    service.tasks = mock_tasks

    result = asyncio.run(service.run_once())

    assert result == 5
    mock_tasks.enqueue_targets.assert_called_once()


