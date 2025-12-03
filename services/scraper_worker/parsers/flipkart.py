import re
import json
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict
from .base_parser import BaseParser

logger = logging.getLogger(__name__)

class FlipkartParser(BaseParser):
    def __init__(self):
        super().__init__("flipkart.com")
        
    def parse_price(self, html: str) -> Optional[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        
        # Strategy 1: Price div
        price_div = soup.select_one('div._30jeq3._16Jk6d')
        if price_div:
            price_text = price_div.get_text().replace(',', '').replace('₹', '').strip()
            try:
                return {
                    "price": float(price_text),
                    "currency": "INR",
                    "method": "css_selector"
                }
            except ValueError:
                pass
        
        # Strategy 2: Alternative selector
        alt_price = soup.select_one('._30jeq3')
        if alt_price:
            price_text = alt_price.get_text().replace(',', '').replace('₹', '').strip()
            try:
                return {
                    "price": float(price_text),
                    "currency": "INR",
                    "method": "alt_selector"
                }
            except ValueError:
                pass
        
        # Strategy 3: JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'offers' in data:
                    price = data['offers'].get('price')
                    if price:
                        return {
                            "price": float(price),
                            "currency": "INR",
                            "method": "json_ld"
                        }
            except:
                continue
        
        logger.warning(f"Could not extract price from {self.domain}")
        return None