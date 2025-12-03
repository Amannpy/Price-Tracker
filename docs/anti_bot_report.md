# Anti-Bot Strategy (MeldIt POC)

This project is a proof-of-concept and is designed to **avoid** aggressive anti-bot evasion. It focuses on responsible, low-volume monitoring.

## Techniques Used

- **Proxy rotation**
  - Health-aware proxy pool with failover
  - Backoff when proxies repeatedly fail
- **User-agent & header entropy**
  - Rotating realistic desktop user agents
  - Varying `Accept-Language`, viewport, and timezone
- **Polite rate limiting**
  - Redis-backed per-domain limits
  - Extra backoff after errors or CAPTCHA encounters
- **CAPTCHA / WAF handling**
  - Detects CAPTCHA-like responses
  - Captures metadata, raises alerts to humans
  - Does **not** implement automated solving or bypass

## Techniques Explicitly Avoided

- Automated CAPTCHA solving
- WAF fingerprint evasion or exploitation
- High-volume crawling that ignores site terms or robots.txt

## Operational Guidance

- Review each target site’s ToS before enabling scraping.
- Keep volumes low and respect rate limits.
- Prefer official APIs or partnerships where available.
- Consult legal counsel for any production or commercial deployment.


