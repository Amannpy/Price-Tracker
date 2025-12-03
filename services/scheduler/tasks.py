import logging
from typing import Dict

from services.scraper_worker.db_manager import DBManager


logger = logging.getLogger(__name__)


class SchedulerTasks:
    """
    Simple scheduler helpers that mark targets as pending scrape jobs.
    Scraper workers later update these rows to success/failure.
    """

    def __init__(self, db_manager: DBManager | None = None):
        self.db = db_manager or DBManager()

    def enqueue_targets(self) -> int:
        """Fetch active targets and mark each as pending."""
        targets = self.db.get_active_targets()
        count = 0
        for target in targets:
            if not target.get("id"):
                continue
            self._mark_job_pending(target)
            count += 1

        logger.info("Scheduler queued %s targets", count)
        return count

    def _mark_job_pending(self, target: Dict):
        target_id = target["id"]
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO scrape_jobs (id, target_id, status, attempts, created_at, updated_at)
                    VALUES (%s, %s, %s, 0, NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE
                    SET status = 'pending',
                        last_error = NULL,
                        updated_at = NOW(),
                        attempts = scrape_jobs.attempts + 1
                    """,
                    (target_id, target_id, "pending"),
                )
        logger.debug("Target %s marked pending", target_id)


