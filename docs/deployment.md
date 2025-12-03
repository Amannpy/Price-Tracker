# Deployment Guide (POC)

## Local (Docker Compose)

1. Copy env:
   - `cp .env.example .env`
2. Start stack:
   - `docker-compose up --build`
3. Dashboard:
   - `http://localhost:8501`

## Kubernetes (Example)

1. Build & push images:
   - `docker build -t your-registry/meldit-scraper:latest .`
   - `docker build -t your-registry/meldit-dashboard:latest -f Dockerfile.dashboard .`
2. Apply manifests:
   - `kubectl apply -f infra/k8s/namespace.yaml`
   - `kubectl apply -f infra/k8s/`
3. Add DNS/hosts entry for `meldit.local` pointing at your ingress controller.

These manifests are intentionally minimal and should be adapted with proper TLS, secrets management, and resource limits before production use.


