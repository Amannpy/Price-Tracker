import hashlib
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class BaseParser:
    def __init__(self, domain: str):
        self.domain = domain
        
    def detect_captcha(self, html: str) -> bool:
        low = html.lower()
        checks = [
            "recaptcha", "g-recaptcha", "captcha",
            "cf-chl-manual-challenge",  # Cloudflare
            "verify you are human",
            "robot check",
            "security check"
        ]
        detected = any(k in low for k in checks)
        if detected:
            logger.warning(f"CAPTCHA detected on {self.domain}")
        return detected
    
    def parse_price(self, html: str) -> Optional[Dict]:
        raise NotImplementedError("Subclass must implement parse_price")
    
    def compute_content_hash(self, html: str) -> str:
        return hashlib.sha256(html.encode()).hexdigest()[:16]
