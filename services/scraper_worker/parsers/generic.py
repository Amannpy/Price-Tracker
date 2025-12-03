from .base_parser import BaseParser
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re


class GenericParser(BaseParser):
    """
    Generic fallback parser that tries a few common patterns:
    - JSON-LD offers
    - meta[itemprop=price]
    - elements with common price classes/ids
    """

    def __init__(self):
        super().__init__("generic")

    def parse_price(self, html: str) -> Optional[Dict]:
        soup = BeautifulSoup(html, "lxml")

        # 1) JSON-LD offers (only if BaseParser or subclass provides a helper)
        helper = getattr(self, "_parse_jsonld_price", None)
        if callable(helper):
            price, currency = helper(soup)
            if price is not None:
                return {"price": price, "currency": currency or "INR"}

        # 2) Common price selectors
        candidates = []
        selectors = [
            "[itemprop=price]",
            ".price",
            ".Price",
            ".sale-price",
            ".a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
        ]
        for sel in selectors:
            candidates.extend(soup.select(sel))

        for node in candidates:
            text = (node.get("content") or node.get_text() or "").strip()
            value = self._extract_price_from_text(text)
            if value is not None:
                return {"price": value, "currency": "INR"}

        return None

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        # Remove currency symbols and non-numeric chars except dot/comma
        cleaned = re.sub(r"[^\d.,]", "", text)
        if not cleaned:
            return None
        # Replace comma thousands separators
        cleaned = cleaned.replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None


