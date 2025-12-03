import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from services.scraper_worker.main import ScraperWorker


def run(coro):
    # Use asyncio.run so tests don't depend on a pre-existing event loop
    return asyncio.run(coro)


@patch("services.scraper_worker.main.redis.from_url")
@patch("services.scraper_worker.main.DBManager")
@patch("services.scraper_worker.main.AlertManager")
@patch("services.scraper_worker.main.PlaywrightDriver")
def test_scrape_target_success(mock_driver_cls, mock_alert_cls, mock_db_cls, mock_redis_from_url):
    # Arrange
    mock_redis = MagicMock()
    mock_redis.exists.return_value = False
    mock_redis_from_url.return_value = mock_redis

    mock_driver = MagicMock()
    mock_driver.fetch_page = AsyncMock(
        return_value={
            "status": 200,
            "html": "<span class='a-price-whole'>1,999</span>",
            "screenshot": None,
            "proxy": "http://proxy",
            "user_agent": "UA",
            "response_time_ms": 123,
        }
    )
    mock_driver_cls.return_value = mock_driver

    mock_db = MagicMock()
    mock_db.get_latest_price.return_value = None  # no prior price → no alert
    mock_db_cls.return_value = mock_db

    mock_alerts = MagicMock()
    mock_alert_cls.return_value = mock_alerts

    worker = ScraperWorker()

    # Use a very simple parser by patching get_parser
    class DummyParser:
        def detect_captcha(self, html: str) -> bool:
            return False

        def parse_price(self, html: str):
            return {"price": 1999.0, "currency": "INR"}

        def compute_content_hash(self, html: str) -> str:
            return "hash"

    worker.get_parser = MagicMock(return_value=DummyParser())

    target = {"id": "t1", "domain": "amazon.in", "url": "https://example.com"}

    # Act
    run(worker.scrape_target(target))

    # Assert
    mock_db.save_price_history.assert_called_once()
    mock_db.update_scrape_job.assert_called_with("t1", "success")
    mock_alerts.alert_price_drop.assert_not_called()
    mock_redis.setex.assert_any_call("rate_limit:amazon.in", 5, "1")


@patch("services.scraper_worker.main.redis.from_url")
@patch("services.scraper_worker.main.DBManager")
@patch("services.scraper_worker.main.AlertManager")
@patch("services.scraper_worker.main.PlaywrightDriver")
def test_scrape_target_captcha_path(mock_driver_cls, mock_alert_cls, mock_db_cls, mock_redis_from_url):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = False
    mock_redis_from_url.return_value = mock_redis

    mock_driver = MagicMock()
    mock_driver.fetch_page = AsyncMock(
        return_value={
            "status": 200,
            "html": "<html>captcha here</html>",
            "screenshot": "screens/s.png",
            "proxy": "http://proxy",
            "user_agent": "UA",
            "response_time_ms": 123,
        }
    )
    mock_driver_cls.return_value = mock_driver

    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db

    mock_alerts = MagicMock()
    mock_alert_cls.return_value = mock_alerts

    worker = ScraperWorker()

    class CaptchaParser:
        def detect_captcha(self, html: str) -> bool:
            return True

        def parse_price(self, html: str):
            return None

        def compute_content_hash(self, html: str) -> str:
            return "hash"

    worker.get_parser = MagicMock(return_value=CaptchaParser())

    target = {"id": "t2", "domain": "amazon.in", "url": "https://example.com"}

    run(worker.scrape_target(target))

    mock_alerts.alert_captcha_encounter.assert_called_once()
    mock_db.update_scrape_job.assert_called_with("t2", "captcha", "CAPTCHA encountered")
    mock_redis.setex.assert_any_call("rate_limit:amazon.in", 300, "1")


@patch("services.scraper_worker.main.redis.from_url")
@patch("services.scraper_worker.main.DBManager")
@patch("services.scraper_worker.main.AlertManager")
@patch("services.scraper_worker.main.PlaywrightDriver")
def test_scrape_target_driver_error_sets_failure(mock_driver_cls, mock_alert_cls, mock_db_cls, mock_redis_from_url):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = False
    mock_redis_from_url.return_value = mock_redis

    mock_driver = MagicMock()
    mock_driver.fetch_page = AsyncMock(side_effect=RuntimeError("network error"))
    mock_driver_cls.return_value = mock_driver

    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db

    mock_alerts = MagicMock()
    mock_alert_cls.return_value = mock_alerts

    worker = ScraperWorker()

    class DummyParser:
        def detect_captcha(self, html: str) -> bool:
            return False

        def parse_price(self, html: str):
            return {"price": 100.0, "currency": "INR"}

        def compute_content_hash(self, html: str) -> str:
            return "hash"

    worker.get_parser = MagicMock(return_value=DummyParser())

    target = {"id": "t3", "domain": "amazon.in", "url": "https://example.com"}

    run(worker.scrape_target(target))

    # Failure path should mark job as failed and set a longer rate limit
    mock_db.update_scrape_job.assert_called()
    status_args = mock_db.update_scrape_job.call_args[0]
    assert status_args[0] == "t3"
    assert status_args[1] == "failed"
    mock_redis.setex.assert_any_call("rate_limit:amazon.in", 30, "1")


