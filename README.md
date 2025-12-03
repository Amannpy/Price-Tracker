# MeldIt E-Commerce Price Intelligence Scraper

Production-grade MVP for continuous price monitoring across Amazon, Flipkart, and competitor sites with comprehensive anti-bot mitigation.

## 🎯 Key Features

- **Multi-site Scraping**: Amazon, Flipkart, and customizable parsers
- **Proxy Rotation**: Automatic proxy health checks and failover
- **Anti-Bot Mitigation**: UA rotation, CAPTCHA detection, human-in-the-loop workflows
- **Real-time Dashboard**: Streamlit UI with price trends and alerts
- **Robust Error Handling**: Exponential backoff, circuit breakers, retry logic
- **Alerting**: Discord/Telegram webhooks for critical events
- **Production-Ready**: Docker, PostgreSQL, Redis, comprehensive logging

## 🏗️ Architecture

```
Scheduler → Scraper Workers (Playwright + Proxies) → Redis (rate limiting)
                ↓                                    ↓
         PostgreSQL (price history)         Alerts (Discord/Telegram)
                ↓
         Streamlit Dashboard
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Python 3.11+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/meldit-scraper.git
cd meldit-scraper
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services:
```bash
docker-compose up -d
```

4. Access dashboard:
```
http://localhost:8501
```

## 📦 Components

### Scraper Worker
- **Location**: `services/scraper_worker/`
- **Tech**: Python, Playwright, asyncio
- **Features**: Proxy rotation, UA randomization, retry logic

### Parsers
- **Amazon**: Multi-strategy parsing (CSS, JSON-LD, meta tags)
- **Flipkart**: Adaptive selectors with fallbacks
- **Extensible**: Easy to add new sites

### Dashboard
- **Tech**: Streamlit, Plotly
- **Features**: Price charts, job monitoring, manual controls

## 🛡️ Anti-Bot Strategy

### What We Handle
1. **Proxy Rotation**: Automatic health checks, failover on errors
2. **User-Agent Randomization**: Diverse UA pool with proper headers
3. **Rate Limiting**: Redis-based per-domain throttling
4. **CAPTCHA Detection**: Automated detection → human review workflow
5. **Request Entropy**: Random delays, viewport variations, stealth scripts

### What We Don't Do
- ❌ Automated CAPTCHA bypass (legal/ToS concerns)
- ❌ Aggressive WAF evasion techniques
- ✅ Instead: Focus on polite crawling, human escalation, API partnerships

## 📊 Database Schema

```sql
products → targets → price_history
         ↓
    scrape_jobs, alerts
```

See `scripts/init_db.sql` for complete schema.

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `PROXY_LIST`: Comma-separated proxy URLs
- `DISCORD_WEBHOOK_URL`: Discord webhook for alerts
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `MAX_RETRIES`: Maximum retry attempts (default: 5)

### Adding New Sites

1. Create parser in `services/scraper_worker/parsers/`:
```python
from .base_parser import BaseParser

class NewSiteParser(BaseParser):
    def __init__(self):
        super().__init__("newsite.com")
    
    def parse_price(self, html: str):
        # Implement parsing logic
        pass
```

2. Register in `main.py`:
```python
self.parsers = {
    'newsite.com': NewSiteParser(),
    ...
}
```

## 📈 Monitoring

### Logs
- Location: `logs/scraper.log`
- Format: JSON structured logs

### Metrics
- Job success/failure rates
- CAPTCHA encounter frequency
- Proxy health statistics
- Response time percentiles

### Alerts
- Price drops/rises (configurable thresholds)
- CAPTCHA encounters (requires manual review)
- Repeated errors (circuit breaker triggered)

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test specific parser
pytest tests/test_parsers.py::test_amazon_parser
```

## 📝 Legal & Compliance

⚠️ **Important**: Web scraping may violate terms of service. Before production use:

1. Review target site ToS
2. Prefer official APIs/data partnerships
3. Implement proper rate limiting
4. Obtain legal counsel if needed

This codebase is for educational/POC purposes. Use responsibly.

## 🎯 Next Steps

- [ ] Kubernetes deployment manifests
- [ ] ML price prediction model
- [ ] Client-facing REST API
- [ ] Role-based access control
- [ ] Expanded site coverage

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Contact

For questions: your.email@example.com
```
