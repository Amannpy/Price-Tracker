import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import Optional, Dict, List
from contextlib import contextmanager
import os
import json

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def save_price_history(self, data: Dict) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO price_history (
                            target_id, price, currency, scraped_at,
                            raw_html, screenshot_url, proxy_used,
                            user_agent, response_time_ms, content_hash
                        ) VALUES (
                            %s, %s, %s, NOW(),
                            %s, %s, %s,
                            %s, %s, %s
                        )
                    """, (
                        data['target_id'],
                        data['price'],
                        data.get('currency', 'INR'),
                        data.get('raw_html'),
                        data.get('screenshot_url'),
                        data.get('proxy_used'),
                        data.get('user_agent'),
                        data.get('response_time_ms'),
                        data.get('content_hash')
                    ))
            logger.info(f"Price history saved for target {data['target_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to save price history: {e}")
            return False
    
    def update_scrape_job(self, job_id: str, status: str, error: str = None):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE scrape_jobs
                        SET status = %s, last_error = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (status, error, job_id))
        except Exception as e:
            logger.error(f"Failed to update scrape job: {e}")
    
    def create_alert(self, product_id: str, alert_type: str, payload: Dict):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO alerts (product_id, alert_type, payload)
                        VALUES (%s, %s, %s::jsonb)
                    """, (product_id, alert_type, json.dumps(payload)))
            logger.info(f"Alert created: {alert_type} for product {product_id}")
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    def get_active_targets(self) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT t.*, p.sku, p.title, p.brand
                        FROM targets t
                        JOIN products p ON t.product_id = p.id
                        WHERE t.active = TRUE
                    """)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch targets: {e}")
            return []
    
    def get_latest_price(self, target_id: str) -> Optional[Dict]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT price, scraped_at
                        FROM price_history
                        WHERE target_id = %s
                        ORDER BY scraped_at DESC
                        LIMIT 1
                    """, (target_id,))
                    return cur.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch latest price: {e}")
            return None
