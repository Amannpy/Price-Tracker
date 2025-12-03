import requests
import logging
import os
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    def send_discord_alert(self, title: str, message: str, color: int = 0xFF0000):
        if not self.discord_webhook:
            logger.warning("Discord webhook not configured")
            return False
        
        try:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
            response = requests.post(self.discord_webhook, json=payload)
            response.raise_for_status()
            logger.info(f"Discord alert sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False
    
    def send_telegram_alert(self, message: str):
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram alert sent")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def alert_captcha_encounter(self, target_info: Dict, screenshot_url: str = None):
        title = "⚠️ CAPTCHA Encountered"
        message = f"""
**Product:** {target_info.get('title', 'Unknown')}
**Domain:** {target_info.get('domain', 'Unknown')}
**URL:** {target_info.get('url', 'N/A')}
**Action Required:** Manual review needed
"""
        if screenshot_url:
            message += f"\n**Screenshot:** {screenshot_url}"
        
        self.send_discord_alert(title, message, color=0xFFA500)
        self.send_telegram_alert(f"{title}\n\n{message}")
    
    def alert_price_drop(self, product_info: Dict, old_price: float, new_price: float):
        drop_percent = ((old_price - new_price) / old_price) * 100
        title = "📉 Price Drop Alert"
        message = f"""
**Product:** {product_info.get('title', 'Unknown')}
**Domain:** {product_info.get('domain', 'Unknown')}
**Old Price:** ₹{old_price:,.2f}
**New Price:** ₹{new_price:,.2f}
**Drop:** {drop_percent:.1f}%
"""
        self.send_discord_alert(title, message, color=0x00FF00)
        self.send_telegram_alert(f"{title}\n\n{message}")
    
    def alert_repeated_errors(self, target_info: Dict, error_count: int):
        title = "❌ Repeated Scraping Errors"
        message = f"""
**Product:** {target_info.get('title', 'Unknown')}
**Domain:** {target_info.get('domain', 'Unknown')}
**Error Count:** {error_count}
**Action Required:** Check target configuration
"""
        self.send_discord_alert(title, message, color=0xFF0000)
        self.send_telegram_alert(f"{title}\n\n{message}")

