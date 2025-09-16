-- ================================
-- DRAM Industry Database Schema (Relational)
-- ================================

-- Drop existing tables in dependency order
DROP TABLE IF EXISTS competitor_pricing;
DROP TABLE IF EXISTS macro_indicators;
DROP TABLE IF EXISTS datacenter_demand;
DROP TABLE IF EXISTS pc_shipments;
DROP TABLE IF EXISTS smartphone_shipments;
DROP TABLE IF EXISTS dram_production;
DROP TABLE IF EXISTS dram_prices;
DROP TABLE IF EXISTS region_dim;
DROP TABLE IF EXISTS date_dim;

-- ================================
-- DIMENSION TABLES
-- ================================

-- Date Dimension
CREATE TABLE date_dim (
    date DATE PRIMARY KEY,
    year INT,
    quarter INT,
    month INT,
    week INT,
    day_of_week_num INT,
    day_of_week_name VARCHAR(10)
);

-- Region Dimension
CREATE TABLE region_dim (
    region_id SERIAL PRIMARY KEY,
    country_code VARCHAR(5) NOT NULL,        -- "AD"
    country_name VARCHAR(100) NOT NULL,      -- "Andorra"
    native_name VARCHAR(100),                -- "Andorra"
    phone_code VARCHAR(20),                  -- "376"
    continent_code VARCHAR(5),               -- "EU"
    continent_name VARCHAR(50),              -- "Europe"
    capital VARCHAR(100),                    -- "Andorra la Vella"
    currency VARCHAR(50),                    -- "EUR"
    languages TEXT                           -- "ca"
);

-- ================================
-- FACT TABLES
-- ================================

-- DRAM Prices
CREATE TABLE dram_prices (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    dram_type VARCHAR(50) NOT NULL,         
    price_usd FLOAT NOT NULL,
    source VARCHAR(100) DEFAULT 'manual',
    CONSTRAINT fk_dram_prices_date FOREIGN KEY (date) REFERENCES date_dim(date)
);

-- DRAM Production
CREATE TABLE dram_production (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    fab_location VARCHAR(100),              
    dram_type VARCHAR(50),
    capacity_million_gb FLOAT,              
    utilization_rate FLOAT,
    CONSTRAINT fk_dram_production_date FOREIGN KEY (date) REFERENCES date_dim(date)
);

-- Smartphone Shipments
CREATE TABLE smartphone_shipments (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    brand VARCHAR(100),                     
    region_id INT,
    shipments_million_units FLOAT,
    CONSTRAINT fk_smartphone_shipments_date FOREIGN KEY (date) REFERENCES date_dim(date),
    CONSTRAINT fk_smartphone_shipments_region FOREIGN KEY (region_id) REFERENCES region_dim(region_id)
);

-- PC Shipments
CREATE TABLE pc_shipments (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    brand VARCHAR(100),                     
    shipments_million_units FLOAT,
    CONSTRAINT fk_pc_shipments_date FOREIGN KEY (date) REFERENCES date_dim(date)
);

-- Datacenter Demand
CREATE TABLE datacenter_demand (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    application VARCHAR(100),               
    demand_million_gb FLOAT,
    CONSTRAINT fk_datacenter_demand_date FOREIGN KEY (date) REFERENCES date_dim(date)
);

-- Macroeconomic Indicators
CREATE TABLE macro_indicators (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    indicator VARCHAR(100),                 
    value FLOAT,
    region_id INT,
    CONSTRAINT fk_macro_indicators_date FOREIGN KEY (date) REFERENCES date_dim(date),
    CONSTRAINT fk_macro_indicators_region FOREIGN KEY (region_id) REFERENCES region_dim(region_id)
);

-- Competitor Pricing
CREATE TABLE competitor_pricing (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    competitor VARCHAR(100),                
    dram_type VARCHAR(50),
    price_usd FLOAT,
    CONSTRAINT fk_competitor_pricing_date FOREIGN KEY (date) REFERENCES date_dim(date)
);

-- ================================
-- INDEXES (for performance)
-- ================================
CREATE INDEX idx_dram_prices_type ON dram_prices(dram_type);
CREATE INDEX idx_dram_production_type ON dram_production(dram_type);
CREATE INDEX idx_smartphone_shipments_brand ON smartphone_shipments(brand);
CREATE INDEX idx_pc_shipments_brand ON pc_shipments(brand);
CREATE INDEX idx_macro_indicators_indicator ON macro_indicators(indicator);
CREATE INDEX idx_competitor_pricing_competitor ON competitor_pricing(competitor);

-- ================================
-- UPDATES
-- ================================

-- Add unique constraint (if not already exists)
ALTER TABLE date_dim 
    ADD CONSTRAINT uq_date_dim_date UNIQUE (date);

ALTER TABLE region_dim 
    ADD CONSTRAINT uq_region_country_code UNIQUE (country_code);
