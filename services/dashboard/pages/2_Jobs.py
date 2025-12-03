import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
import psycopg2
import os


st.set_page_config(page_title="Jobs", page_icon="⚙️")


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def fetch_jobs(limit: int = 200):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT j.*, t.domain, t.url
                FROM scrape_jobs j
                LEFT JOIN targets t ON j.target_id = t.id
                ORDER BY j.created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()
    finally:
        conn.close()


st.title("⚙️ Scrape Jobs")

rows = fetch_jobs()
if not rows:
    st.info("No scrape jobs recorded yet.")
else:
    df = pd.DataFrame(rows)
    st.dataframe(
        df[
            [
                "status",
                "attempts",
                "last_error",
                "domain",
                "url",
                "created_at",
                "updated_at",
            ]
        ]
    )


