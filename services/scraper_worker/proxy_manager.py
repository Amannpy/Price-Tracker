import random
import time
import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProxyHealth:
    proxy: str
    failures: int = 0
    last_failure: float = 0.0
    last_success: float = 0.0

class ProxyManager:
    def __init__(self, proxies: List[str], health_check_interval: int = 60):
        self.proxies = proxies[:]
        self._health = {p: ProxyHealth(proxy=p) for p in proxies}
        self.health_check_interval = health_check_interval
        self._bad_threshold = 3
        self._recovery_time = 300
        
    def get_proxy(self) -> Optional[str]:
        # Filter out proxies with recent failures
        now = time.time()
        candidates = [
            p for p, health in self._health.items()
            if health.failures < self._bad_threshold or 
               (now - health.last_failure > self._recovery_time)
        ]
        
        if not candidates:
            logger.warning("No healthy proxies available, using any proxy")
            candidates = list(self.proxies)
            
        proxy = random.choice(candidates)
        logger.debug(f"Selected proxy: {proxy[:20]}...")
        return proxy

    def mark_failure(self, proxy: str, error: str = None):
        if proxy in self._health:
            self._health[proxy].failures += 1
            self._health[proxy].last_failure = time.time()
            logger.warning(f"Proxy failure marked: {proxy[:20]}... (total failures: {self._health[proxy].failures})")
            if error:
                logger.error(f"Failure reason: {error}")
    
    def mark_success(self, proxy: str):
        if proxy in self._health:
            self._health[proxy].failures = max(0, self._health[proxy].failures - 1)
            self._health[proxy].last_success = time.time()
            logger.debug(f"Poxy success: {proxy[:20]}...")
    
    def get_health_stats(self) -> dict:
        healthy = sum(1 for h in self._health.values() if h.failures < self._bad_threshold)
        return {
            "total": len(self.proxies),
            "healthy": healthy,
            "degraded": len(self.proxies) - healthy
        }