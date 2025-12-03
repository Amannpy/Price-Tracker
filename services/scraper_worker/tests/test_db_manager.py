from unittest.mock import MagicMock, patch

from services.scraper_worker.db_manager import DBManager


@patch("services.scraper_worker.db_manager.psycopg2.connect")
def test_save_price_history_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = DBManager(connection_string="postgres://test")
    ok = db.save_price_history(
        {
            "target_id": "t1",
            "price": 123.45,
            "currency": "INR",
            "raw_html": "<html/>",
            "screenshot_url": None,
            "proxy_used": "proxy",
            "user_agent": "UA",
            "response_time_ms": 100,
            "content_hash": "hash",
        }
    )

    assert ok is True
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("services.scraper_worker.db_manager.psycopg2.connect")
def test_save_price_history_failure_returns_false(mock_connect):
    # Force connect failure
    mock_connect.side_effect = RuntimeError("db down")
    db = DBManager(connection_string="postgres://test")
    ok = db.save_price_history(
        {
            "target_id": "t1",
            "price": 123.45,
        }
    )
    assert ok is False


@patch("services.scraper_worker.db_manager.psycopg2.connect")
def test_update_scrape_job_executes_update(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = DBManager(connection_string="postgres://test")
    db.update_scrape_job("job-1", "success", None)

    mock_cursor.execute.assert_called_once()


@patch("services.scraper_worker.db_manager.psycopg2.connect")
def test_create_alert_inserts_payload(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = DBManager(connection_string="postgres://test")
    db.create_alert("prod-1", "price_drop", {"old": 100, "new": 90})

    mock_cursor.execute.assert_called_once()


@patch("services.scraper_worker.db_manager.psycopg2.connect")
def test_get_active_targets_returns_list(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": "t1"}, {"id": "t2"}]

    db = DBManager(connection_string="postgres://test")
    rows = db.get_active_targets()

    assert len(rows) == 2
    mock_cursor.execute.assert_called_once()


@patch("services.scraper_worker.db_manager.psycopg2.connect")
def test_get_latest_price_returns_row(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"price": 123.45}

    db = DBManager(connection_string="postgres://test")
    row = db.get_latest_price("t1")

    assert row["price"] == 123.45
    mock_cursor.execute.assert_called_once()


