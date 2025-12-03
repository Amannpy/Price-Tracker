from fastapi import APIRouter
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from ..models import Product


router = APIRouter()


@contextmanager
def get_conn():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    try:
        yield conn
    finally:
        conn.close()


@router.get("/", response_model=List[Product])
def list_products():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, sku, title, brand, created_at
                FROM products
                ORDER BY created_at DESC
                """
            )
            rows = cur.fetchall()
            return rows


