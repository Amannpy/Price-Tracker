import asyncio
import random
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional, Dict

# Support both package and script-style imports for tests / runtime
try:
    from .retry_decorator import retry_backoff
except ImportError:
    from retry_decorator import retry_backoff

logger = logging.getLogger(__name__)

class PlaywrightDriver:
    def __init__(self, proxy_manager, ua_manager):
        self.proxy_manager = proxy_manager
        self.ua_manager = ua_manager
        
    @retry_backoff(max_attempts=3, base=2.0)
    async def fetch_page(
        self, 
        url: str, 
        timeout: int = 30000,
        wait_for_selector: Optional[str] = None
    ) -> Dict:
        proxy = self.proxy_manager.get_proxy()
        user_agent = self.ua_manager.pick_ua()
        
        start_time = asyncio.get_event_loop().time()
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context_args = {
                    "user_agent": user_agent,
                    "viewport": {
                        "width": random.randint(1200, 1920),
                        "height": random.randint(800, 1080)
                    },
                    "locale": "en-IN",
                    "timezone_id": "Asia/Kolkata",
                }
                
                if proxy:
                    context_args["proxy"] = {"server": proxy}
                
                context = await browser.new_context(**context_args)
                
                # Add stealth scripts
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page = await context.new_page()
                
                try:
                    response = await page.goto(url, timeout=timeout, wait_until='domcontentloaded')
                    
                    # Wait for specific selector if provided
                    if wait_for_selector:
                        await page.wait_for_selector(wait_for_selector, timeout=10000)
                    
                    # Random delay to simulate human behavior
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                    html = await page.content()
                    status = response.status if response else None
                    
                    response_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
                    
                    # Take screenshot if needed
                    screenshot_path = None
                    if status and status >= 400:
                        screenshot_path = f"screenshots/error_{int(start_time)}.png"
                        await page.screenshot(path=screenshot_path)
                    
                    self.proxy_manager.mark_success(proxy)
                    
                    return {
                        "status": status,
                        "html": html,
                        "screenshot": screenshot_path,
                        "proxy": proxy,
                        "user_agent": user_agent,
                        "response_time_ms": response_time
                    }
                    
                finally:
                    await context.close()
                    await browser.close()
                    
            except Exception as e:
                self.proxy_manager.mark_failure(proxy, str(e))
                raise
