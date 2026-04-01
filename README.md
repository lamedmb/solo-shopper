# Solo Shopper - Personal Grocery Intelligence System

> Applying retail analytics methods to single-person household grocery purchasing

## What It Does

**Solo Shopper** is an end-to-end analytics system that:
- Tracks grocery prices across Tesco and Sainsbury's to find the best deals
- Detects "anchor pricing" (fake Clubcard discounts)
- Logs what you actually consume vs. waste
- Forecasts your weekly demand for each item
- Generates optimized shopping lists (what to buy, how much, from where)

## Modules

### 1. Price Intelligence
Automated weekly scraper tracking 50+ products with promotional discount analysis

### 2. Consumption & Waste Tracker  
Personal logging system quantifying true cost-per-consumed-unit

### 3. Smart Shopping Recommender
ML-based demand forecasting + EOQ optimization for pack size recommendations

## Tech Stack

- **Python** - pandas, BeautifulSoup/Playwright, Prophet, scipy
- **PostgreSQL** (Supabase) - relational database with proper schema
- **SQL** - window functions, CTEs, joins
- **Streamlit** - interactive dashboard
- **GitHub Actions** - automated weekly data pipelines

## Project Structure
```
solo-shopper/
├── data/
│   ├── raw/          # Receipt logs, scraped data
│   └── processed/    # Cleaned, analysis-ready data
├── src/
│   ├── scraper/      # Price scraping modules
│   ├── database/     # DB schema, connection handlers
│   ├── analysis/     # Consumption & waste analysis
│   ├── forecasting/  # Demand forecasting models
│   └── app/          # Streamlit dashboard
├── notebooks/        # Exploratory analysis
├── tests/            # Unit tests
└── docs/             # Documentation
```

## Getting Started

See [docs/setup.md](docs/setup.md) for installation instructions.

## Current Status

- [x] Phase 1: Setup & synthetic data generation
- [ ] Phase 2: Database design & setup
- [ ] Phase 3: Price scraper
- [ ] Phase 4: Streamlit app MVP
- [ ] Phase 5: Real data collection (6-8 weeks)
- [ ] Phase 6: Forecasting & optimization

---

**Author:** Lohla Bui  
**Start Date:** April 2026  
