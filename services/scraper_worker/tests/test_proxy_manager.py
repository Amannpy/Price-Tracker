import pytest

from services.scraper_worker.proxy_manager import ProxyManager


def test_proxy_manager_health_stats():
    proxies = ["http://proxy1", "http://proxy2"]
    mgr = ProxyManager(proxies)

    stats = mgr.get_health_stats()
    assert stats["total"] == 2
    assert stats["healthy"] == 2

    mgr.mark_failure("http://proxy1")
    stats2 = mgr.get_health_stats()
    assert stats2["total"] == 2



