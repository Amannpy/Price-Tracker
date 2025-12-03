from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    sku: str
    title: Optional[str]
    brand: Optional[str]
    created_at: datetime


class Target(BaseModel):
    id: str
    product_id: str
    domain: str
    url: str
    active: bool


class ScrapeJob(BaseModel):
    id: str
    target_id: Optional[str]
    status: Optional[str]
    attempts: int
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime


