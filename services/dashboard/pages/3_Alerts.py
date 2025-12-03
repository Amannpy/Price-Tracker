import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import psycopg2
import os


st.set_page_config(page_title="Alerts", page_icon="🚨")


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def fetch_alerts():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT a.*, p.sku, p.title AS product_title
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                ORDER BY a.created_at DESC
                LIMIT 200
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


st.title("🚨 Alerts")

rows = fetch_alerts()
if not rows:
    st.info("No alerts recorded.")
else:
    df = pd.DataFrame(rows)
    st.dataframe(
        df[
            [
                "alert_type",
                "resolved",
                "product_title",
                "sku",
                "created_at",
            ]
        ]
    )


