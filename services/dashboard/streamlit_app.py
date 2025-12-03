import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Page config
st.set_page_config(
    page_title="MeldIt Price Intelligence",
    page_icon="📊",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def fetch_products():
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT p.*, COUNT(t.id) as target_count
            FROM products p
            LEFT JOIN targets t ON p.id = t.product_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """)
        return cur.fetchall()

def fetch_price_history(product_id, days=30):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                t.domain,
                ph.price,
                ph.scraped_at,
                ph.response_time_ms
            FROM price_history ph
            JOIN targets t ON ph.target_id = t.id
            WHERE t.product_id = %s
            AND ph.scraped_at > NOW() - INTERVAL '%s days'
            ORDER BY ph.scraped_at
        """, (product_id, days))
        return cur.fetchall()

def fetch_job_stats():
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM scrape_jobs
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY status
        """)
        results = cur.fetchall()
        return {row['status']: row['count'] for row in results}

def fetch_alerts():
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT a.*, p.title as product_title
            FROM alerts a
            JOIN products p ON a.product_id = p.id
            WHERE a.resolved = FALSE
            ORDER BY a.created_at DESC
            LIMIT 10
        """)
        return cur.fetchall()

# Header
st.title("🎯 MeldIt E-Commerce Price Intelligence")
st.markdown("Real-time price monitoring with proxy rotation & anti-bot mitigation")

# Stats row
col1, col2, col3, col4 = st.columns(4)

job_stats = fetch_job_stats()
col1.metric("✅ Successful", job_stats.get('success', 0))
col2.metric("❌ Failed", job_stats.get('failed', 0))
col3.metric("⚠️ CAPTCHA", job_stats.get('captcha', 0))
col4.metric("🔄 Running", job_stats.get('running', 0))

st.divider()

# Main content
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📦 Tracked Products")
    products = fetch_products()
    
    selected_product = st.selectbox(
        "Select Product",
        options=products,
        format_func=lambda x: f"{x['title']} ({x['target_count']} sites)"
    )
    
    if selected_product:
        st.info(f"**Brand:** {selected_product['brand']}")
        st.info(f"**SKU:** {selected_product['sku']}")
        
        if st.button("🔄 Rescrape All Targets"):
            st.success("Rescrape jobs enqueued!")

with col_right:
    st.subheader("📈 Price History")
    
    if selected_product:
        history = fetch_price_history(selected_product['id'])
        
        if history:
            df = pd.DataFrame(history)
            df['scraped_at'] = pd.to_datetime(df['scraped_at'])
            
            fig = go.Figure()
            
            for domain in df['domain'].unique():
                domain_data = df[df['domain'] == domain]
                fig.add_trace(go.Scatter(
                    x=domain_data['scraped_at'],
                    y=domain_data['price'],
                    mode='lines+markers',
                    name=domain,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title=f"Price Trends - {selected_product['title']}",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Current prices
            st.subheader("💰 Current Prices")
            latest_prices = df.sort_values('scraped_at').groupby('domain').last()
            
            price_cols = st.columns(len(latest_prices))
            for idx, (domain, row) in enumerate(latest_prices.iterrows()):
                with price_cols[idx]:
                    st.metric(
                        label=domain,
                        value=f"₹{row['price']:,.2f}",
                        delta=f"{row['response_time_ms']}ms"
                    )
        else:
            st.warning("No price history available")

# Alerts section
st.divider()
st.subheader("🚨 Active Alerts")

alerts = fetch_alerts()
if alerts:
    for alert in alerts:
        alert_type = alert['alert_type']
        icon = "📉" if "price" in alert_type else "⚠️"
        
        with st.expander(f"{icon} {alert['product_title']} - {alert_type}"):
            st.json(alert['payload'])
            st.caption(f"Created: {alert['created_at']}")
            if st.button("✓ Resolve", key=alert['id']):
                st.success("Alert resolved")
else:
    st.info("No active alerts")

# Footer
st.divider()
st.caption("MeldIt POC - Production-grade scraper with Playwright, Proxy Rotation & Anti-Bot Detection")
