-- Products table: canonical product tracked across domains
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sku TEXT NOT NULL UNIQUE,
  title TEXT,
  description TEXT,
  brand TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Targets: site-specific product landing to scrape
CREATE TABLE IF NOT EXISTS targets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  domain TEXT NOT NULL,
  url TEXT NOT NULL,
  site_sku TEXT,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(product_id, domain)
);

-- Price history
CREATE TABLE IF NOT EXISTS price_history (
  id BIGSERIAL PRIMARY KEY,
  target_id UUID REFERENCES targets(id) ON DELETE CASCADE,
  price NUMERIC(12,2) NOT NULL,
  currency TEXT DEFAULT 'INR',
  scraped_at TIMESTAMPTZ NOT NULL,
  raw_html TEXT,
  screenshot_url TEXT,
  proxy_used TEXT,
  user_agent TEXT,
  response_time_ms INT,
  content_hash TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Scraper job log / audit
CREATE TABLE IF NOT EXISTS scrape_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  target_id UUID REFERENCES targets(id),
  status TEXT,
  attempts INT DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id),
  alert_type TEXT,
  payload JSONB,
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_price_history_target_scraped ON price_history(target_id, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_scrape_jobs_status ON scrape_jobs(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_payload ON alerts USING GIN(payload);

-- Insert sample data
INSERT INTO products (sku, title, brand) VALUES
  ('PHONE-001', 'Samsung Galaxy S24', 'Samsung'),
  ('LAPTOP-001', 'MacBook Pro 14"', 'Apple'),
  ('TV-001', 'Sony Bravia 55" 4K', 'Sony')
ON CONFLICT (sku) DO NOTHING;

-- Add sample targets
INSERT INTO targets (product_id, domain, url, site_sku) 
SELECT 
  p.id,
  'amazon.in',
  'https://www.amazon.in/dp/B0EXAMPLE',
  'B0EXAMPLE'
FROM products p WHERE p.sku = 'PHONE-001'
ON CONFLICT DO NOTHING;
