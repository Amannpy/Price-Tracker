# Operations Runbook (POC)

## Common Tasks

- **Restart scraper worker**
  - Docker Compose: `docker-compose restart scraper`
  - Kubernetes: `kubectl rollout restart deploy/meldit-scraper -n meldit`

- **Check logs**
  - Scraper: `docker-compose logs -f scraper` or `kubectl logs deploy/meldit-scraper -n meldit`
  - Dashboard: `docker-compose logs -f dashboard` or `kubectl logs deploy/meldit-dashboard -n meldit`

## Incident Examples

- **CAPTCHA spike**
  - Look at alerts in Discord/Telegram.
  - Consider temporarily increasing scrape interval and reducing concurrency.
  - Manually check the target pages and adjust configuration.

- **Repeated failures on one domain**
  - Inspect `scrape_jobs` and recent logs.
  - Validate target URLs and selectors.
  - Check proxy health and rotate credentials if needed.

## Safety Notes

- Keep scraping volumes low and respect ToS/robots.txt.
- Prefer API integrations or partnerships where possible.
- Do not introduce automated CAPTCHA solving into this POC.


