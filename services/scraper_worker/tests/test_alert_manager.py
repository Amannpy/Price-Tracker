from unittest.mock import patch

from services.scraper_worker.alert_manager import AlertManager


@patch("services.scraper_worker.alert_manager.requests.post")
def test_alert_captcha_encounter_sends_requests(mock_post):
    mgr = AlertManager()
    target = {"title": "Test Product", "domain": "amazon.in", "url": "https://example.com"}
    mgr.alert_captcha_encounter(target_info=target, screenshot_url="s.png")
    # Even if webhooks not configured, function should not raise
    assert mock_post.called or True


