import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import psycopg2
import os


st.set_page_config(page_title="Products", page_icon="📦")


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def fetch_products():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT p.*, COUNT(t.id) AS target_count
                FROM products p
                LEFT JOIN targets t ON p.id = t.product_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


st.title("📦 Products")

rows = fetch_products()
if not rows:
    st.info("No products found in the database.")
else:
    df = pd.DataFrame(rows)
    st.dataframe(df[["sku", "title", "brand", "target_count", "created_at"]])


