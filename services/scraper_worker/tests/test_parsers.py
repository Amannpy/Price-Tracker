from services.scraper_worker.parsers.amazon import AmazonParser
from services.scraper_worker.parsers.flipkart import FlipkartParser
from services.scraper_worker.parsers.generic import GenericParser


def test_amazon_parser_css_selector():
    html = """
    <span class="a-price-whole">1,999</span>
    """
    parser = AmazonParser()
    result = parser.parse_price(html)
    assert result is not None
    assert result["price"] == 1999.0
    assert result["currency"] == "INR"


def test_flipkart_parser_primary_selector():
    html = """
    <div class="_30jeq3 _16Jk6d">₹2,499</div>
    """
    parser = FlipkartParser()
    result = parser.parse_price(html)
    assert result is not None
    assert result["price"] == 2499.0


def test_generic_parser_fallback_selector():
    html = """
    <div class="price">₹3,499</div>
    """
    parser = GenericParser()
    result = parser.parse_price(html)
    assert result is not None
    assert result["price"] == 3499.0


