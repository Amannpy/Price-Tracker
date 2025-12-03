from fastapi import FastAPI

from .routes import products, targets, jobs


app = FastAPI(
    title="MeldIt Scraper API",
    version="0.1.0",
    description="Read-only API for products, targets, and scrape jobs.",
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(targets.router, prefix="/targets", tags=["targets"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])


