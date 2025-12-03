from fastapi import APIRouter
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from ..models import ScrapeJob


router = APIRouter()


@contextmanager
def get_conn():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    try:
        yield conn
    finally:
        conn.close()


@router.get("/", response_model=List[ScrapeJob])
def list_jobs(limit: int = 100):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, target_id, status, attempts, last_error, created_at, updated_at
                FROM scrape_jobs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return rows


