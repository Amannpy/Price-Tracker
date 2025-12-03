from unittest.mock import MagicMock, patch

from services.scheduler.tasks import SchedulerTasks


@patch("services.scheduler.tasks.DBManager")
def test_enqueue_targets_marks_each_pending(mock_db_cls):
    mock_db = MagicMock()
    mock_db.get_active_targets.return_value = [{"id": "t1"}, {"id": "t2"}]
    mock_db_cls.return_value = mock_db

    tasks = SchedulerTasks()
    tasks._mark_job_pending = MagicMock()

    count = tasks.enqueue_targets()

    assert count == 2
    tasks._mark_job_pending.assert_any_call({"id": "t1"})
    tasks._mark_job_pending.assert_any_call({"id": "t2"})


@patch("services.scheduler.tasks.DBManager")
def test_mark_job_pending_upserts_job(mock_db_cls):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_db = MagicMock()
    mock_db.get_connection.return_value.__enter__.return_value = mock_conn
    mock_db_cls.return_value = mock_db

    tasks = SchedulerTasks()
    tasks._mark_job_pending({"id": "t1"})

    mock_cursor.execute.assert_called_once()


