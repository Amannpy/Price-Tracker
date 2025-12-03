import asyncio
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Support both "python services/scraper_worker/main.py" and imports via package
try:  # package-relative imports (for tests, python -m)
    from .proxy_manager import ProxyManager
    from .ua_manager import pick_ua, get_random_headers
    from .playwright_driver import PlaywrightDriver
    from .parsers.amazon import AmazonParser
    from .parsers.flipkart import FlipkartParser
    from .parsers.generic import GenericParser
    from .db_manager import DBManager
    from .alert_manager import AlertManager
except ImportError:  # script-style fallback
    from proxy_manager import ProxyManager
    from ua_manager import pick_ua, get_random_headers
    from playwright_driver import PlaywrightDriver
    from parsers.amazon import AmazonParser
    from parsers.flipkart import FlipkartParser
    from parsers.generic import GenericParser
    from db_manager import DBManager
    from alert_manager import AlertManager
import redis
from prometheus_client import Counter, Gauge, start_http_server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/scraper.log')
    ]
)
logger = logging.getLogger(__name__)

SCRAPE_SUCCESS = Counter("scraper_success_total", "Number of successful scrapes", ["domain"])
SCRAPE_FAILURE = Counter("scraper_failure_total", "Number of failed scrapes", ["domain"])
SCRAPE_CAPTCHA = Counter("scraper_captcha_total", "Number of captcha encounters", ["domain"])
SCRAPE_DURATION = Gauge("scraper_last_duration_seconds", "Duration of last scrape per domain", ["domain"])


class ScraperWorker:
    def __init__(self):
        # Initialize components
        proxy_list = os.getenv('PROXY_LIST', '').split(',')
        self.proxy_manager = ProxyManager(proxy_list) if proxy_list[0] else None
        self.driver = PlaywrightDriver(self.proxy_manager, type('UA', (), {'pick_ua': pick_ua})())
        self.db = DBManager()
        self.alerts = AlertManager()
        
        # Redis for rate limiting and locks
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis = redis.from_url(redis_url, decode_responses=True)
        
        # Parser registry
        generic = GenericParser()
        self.parsers = {
            'amazon.in': AmazonParser(),
            'flipkart.com': FlipkartParser(),
            # Fallback for any other domain
            '*': generic,
        }
        
    def get_parser(self, domain: str):
        # Exact match, else fallback to generic parser if configured
        return self.parsers.get(domain) or self.parsers.get("*")
    
    async def scrape_target(self, target: dict):
        target_id = target['id']
        domain = target['domain']
        url = target['url']
        
        logger.info(f"Scraping target {target_id}: {domain}")
        
        # Check rate limit
        rate_limit_key = f"rate_limit:{domain}"
        if self.redis.exists(rate_limit_key):
            wait_time = self.redis.ttl(rate_limit_key)
            logger.info(f"Rate limited for {domain}, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
        
        try:
            start_time = asyncio.get_event_loop().time()
            # Fetch page
            result = await self.driver.fetch_page(url)
            html = result['html']
            status = result['status']
            
            # Get appropriate parser
            parser = self.get_parser(domain)
            if not parser:
                logger.error(f"No parser for domain: {domain}")
                return
            
            # Check for CAPTCHA
            if parser.detect_captcha(html):
                logger.warning(f"CAPTCHA detected for target {target_id}")
                self.alerts.alert_captcha_encounter(target, result.get('screenshot'))
                self.db.update_scrape_job(target_id, 'captcha', 'CAPTCHA encountered')
                # Set longer rate limit after CAPTCHA
                self.redis.setex(rate_limit_key, 300, "1")
                return
            
            # Parse price
            price_data = parser.parse_price(html)
            if not price_data:
                logger.error(f"Could not parse price for target {target_id}")
                self.db.update_scrape_job(target_id, 'failed', 'Price parsing failed')
                return
            
            # Check for price drop
            latest_price = self.db.get_latest_price(target_id)
            if latest_price and price_data['price'] < latest_price['price'] * 0.95:
                self.alerts.alert_price_drop(
                    target,
                    latest_price['price'],
                    price_data['price']
                )
            
            # Save to database
            save_data = {
                'target_id': target_id,
                'price': price_data['price'],
                'currency': price_data['currency'],
                'raw_html': html[:5000],  # Store first 5000 chars
                'screenshot_url': result.get('screenshot'),
                'proxy_used': result.get('proxy'),
                'user_agent': result.get('user_agent'),
                'response_time_ms': result.get('response_time_ms'),
                'content_hash': parser.compute_content_hash(html)
            }
            
            self.db.save_price_history(save_data)
            self.db.update_scrape_job(target_id, 'success')
            SCRAPE_SUCCESS.labels(domain=domain).inc()
            SCRAPE_DURATION.labels(domain=domain).set(asyncio.get_event_loop().time() - start_time)
            
            # Set normal rate limit
            self.redis.setex(rate_limit_key, 5, "1")
            
            logger.info(f"Successfully scraped {domain}: ₹{price_data['price']}")
            
        except Exception as e:
            logger.error(f"Error scraping target {target_id}: {e}")
            self.db.update_scrape_job(target_id, 'failed', str(e))
            SCRAPE_FAILURE.labels(domain=domain).inc()
            # Set rate limit on error
            self.redis.setex(rate_limit_key, 30, "1")
    
    async def run(self):
        logger.info("Scraper worker starting...")
        
        while True:
            try:
                # Get active targets from database
                targets = self.db.get_active_targets()
                logger.info(f"Found {len(targets)} active targets")
                
                # Scrape each target
                for target in targets:
                    try:
                        await self.scrape_target(target)
                        # Polite delay between targets
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Failed to scrape target {target['id']}: {e}")
                        continue
                
                # Wait before next round
                logger.info("Scrape round completed, waiting 60 seconds...")
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(10)

if __name__ == "__main__":
    worker = ScraperWorker()
    start_http_server(int(os.getenv("SCRAPER_METRICS_PORT", "8001")))
    asyncio.run(worker.run())
