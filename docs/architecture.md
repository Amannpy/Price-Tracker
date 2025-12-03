# MeldIt Scraper Architecture

This document complements the README and describes how the main components fit together.

## High-Level Diagram

Scheduler → Scraper Workers (Playwright + Proxies) → Redis (rate limiting)
               ↓                                    ↓
        PostgreSQL (price history)           Alerts (Discord/Telegram)
               ↓
        Streamlit Dashboard / FastAPI API

## Components

- **Scraper worker (`services/scraper_worker`)**
  - Playwright-driven browser scraping
  - Proxy rotation and UA/header entropy
  - Redis-based per-domain rate limiting
  - Writes `price_history`, updates `scrape_jobs`, and creates `alerts`
- **API (`services/api`)**
  - FastAPI app exposing read-only endpoints for products, targets, and jobs
- **Dashboard (`services/dashboard`)**
  - Streamlit app for price charts, job status, and alerts
- **Database (`scripts/init_db.sql`)**
  - Postgres schema for `products`, `targets`, `price_history`, `scrape_jobs`, `alerts`
- **Infra (`infra/k8s`)**
  - Example namespace, deployments, service, ingress, secrets


