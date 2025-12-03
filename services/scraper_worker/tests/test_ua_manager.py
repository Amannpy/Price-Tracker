from services.scraper_worker.ua_manager import pick_ua, get_random_headers


def test_pick_ua_returns_string():
    ua = pick_ua()
    assert isinstance(ua, str)
    assert "Mozilla" in ua


def test_get_random_headers_contains_accept_language():
    headers = get_random_headers()
    assert "Accept-Language" in headers
    assert headers["Accept-Language"]


