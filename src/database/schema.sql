-- Solo Shopper Database Schema
-- PostgreSQL / Supabase

-- 1. Products master table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    typical_shelf_life_days INTEGER,
    base_price_gbp DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Price history (scraped weekly)
CREATE TABLE IF NOT EXISTS price_history (
    price_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product_id INTEGER REFERENCES products(product_id),
    store VARCHAR(50) NOT NULL,
    regular_price DECIMAL(6,2) NOT NULL,
    promotional_price DECIMAL(6,2),
    promotion_type VARCHAR(100),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, product_id, store)
);

-- 3. Purchases (your actual shopping trips)
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product_id INTEGER REFERENCES products(product_id),
    store VARCHAR(50) NOT NULL,
    price_paid DECIMAL(6,2) NOT NULL,
    promotional_price_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Consumption & waste log (filled weekly)
CREATE TABLE IF NOT EXISTS consumption_log (
    log_id SERIAL PRIMARY KEY,
    purchase_id INTEGER REFERENCES purchases(purchase_id),
    week_ending DATE NOT NULL,
    proportion_consumed DECIMAL(3,2) NOT NULL CHECK (proportion_consumed >= 0 AND proportion_consumed <= 1),
    proportion_wasted DECIMAL(3,2) NOT NULL CHECK (proportion_wasted >= 0 AND proportion_wasted <= 1),
    waste_reason VARCHAR(200),
    waste_cost_gbp DECIMAL(6,2),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT consumption_adds_up CHECK (proportion_consumed + proportion_wasted = 1)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(date);
CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(date);
CREATE INDEX IF NOT EXISTS idx_consumption_week ON consumption_log(week_ending);

-- View: Latest prices by store
CREATE OR REPLACE VIEW latest_prices AS
SELECT DISTINCT ON (ph.product_id, ph.store)
    p.name AS product_name,
    ph.product_id,
    ph.store,
    ph.regular_price,
    ph.promotional_price,
    ph.promotion_type,
    ph.date AS price_date
FROM price_history ph
JOIN products p ON ph.product_id = p.product_id
ORDER BY ph.product_id, ph.store, ph.date DESC;

-- View: Weekly spending summary
CREATE OR REPLACE VIEW weekly_spending AS
SELECT 
    date,
    store,
    COUNT(*) AS items_bought,
    SUM(price_paid) AS total_spent
FROM purchases
GROUP BY date, store
ORDER BY date DESC;

-- View: Waste analysis by category
CREATE OR REPLACE VIEW waste_by_category AS
SELECT 
    p.category,
    COUNT(*) AS purchases,
    ROUND(AVG(cl.proportion_wasted), 2) AS avg_waste_rate,
    SUM(cl.waste_cost_gbp) AS total_waste_cost
FROM consumption_log cl
JOIN purchases pur ON cl.purchase_id = pur.purchase_id
JOIN products p ON pur.product_id = p.product_id
GROUP BY p.category
ORDER BY total_waste_cost DESC;