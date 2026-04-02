# 🛒 Solo Shopper - Personal Grocery Intelligence System

> Applying retail analytics methods to single-person household grocery purchasing

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen)](https://solo-shopper-lohla.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Problem Statement

Most grocery analytics is built for average households of 2.4 people. **Solo Shopper** applies retail price intelligence, consumption forecasting, and supply chain optimization to the underserved single-person household market.

## 📊 Key Features

### 1. **Price Intelligence**
- Manual price tracking across Tesco and Sainsbury's
- Promotional price analysis (Clubcard/Nectar detection)
- Historical price trends and store comparisons

### 2. **Consumption & Waste Analytics**
- Weekly consumption logging system
- Waste quantification by category
- True cost-per-consumed-unit calculation
- Waste reason analysis (expired, over-bought, didn't cook as planned)

### 3. **Demand Forecasting**
- Exponential smoothing forecasting model
- Predicts weekly consumption patterns with 3+ weeks of data
- Confidence scoring based on data availability
- Trend detection (increasing/decreasing consumption)

### 4. **EOQ Optimization**
- Economic Order Quantity calculations
- Optimal purchase frequency recommendations
- Waste risk assessment (HIGH/MEDIUM/LOW)
- Pack size optimization based on shelf life and consumption rate

### 5. **Smart Shopping List**
- AI-generated weekly shopping lists
- Prioritized by consumption urgency
- Waste risk warnings
- Cost-per-week optimization

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web App                        │
│  (Mobile-optimized UI deployed on Streamlit Cloud)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Python Backend Layer                       │
│  • Forecasting (exponential smoothing, statsmodels)         │
│  • EOQ Optimization (scipy)                                  │
│  • Data Processing (pandas, numpy)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (Supabase)                  │
│  • Products master table                                     │
│  • Price history (date, store, regular/promo prices)        │
│  • Purchases log (with expiry dates)                         │
│  • Consumption log (weekly consumption & waste)              │
└─────────────────────────────────────────────────────────────┘
```

## 💻 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive dashboard & mobile UI |
| **Backend** | Python 3.11 | Data processing & analytics |
| **Database** | PostgreSQL (Supabase) | Relational data storage |
| **Forecasting** | statsmodels, scikit-learn | Time series forecasting |
| **Optimization** | scipy | EOQ calculations |
| **Visualization** | matplotlib, seaborn | Charts & graphs |
| **Deployment** | Streamlit Cloud | Cloud hosting |

## 📁 Project Structure
```
solo-shopper/
├── data/
│   └── raw/              # Synthetic data for testing
├── src/
│   ├── app/              # Streamlit application
│   │   ├── Home.py       # Main entry point
│   │   └── pages/        # Multi-page app
│   │       ├── log_purchase.py    # Purchase logging
│   │       ├── log_waste.py       # Waste tracking
│   │       ├── add_product.py     # Product management
│   │       └── dashboard.py       # Analytics dashboard
│   ├── database/         # Database layer
│   │   ├── schema.sql
│   │   ├── db_connection.py
│   │   └── load_data.py
│   ├── forecasting/      # ML & optimization
│   │   ├── consumption_forecast.py
│   │   └── eoq_optimizer.py
│   └── scraper/          # Price scraping (prototype)
│       ├── tesco_scraper.py
│       ├── sainsburys_scraper.py
│       └── manual_price_entry.py
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11
- Supabase account (free tier)

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/solo-shopper.git
cd solo-shopper

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with your Supabase credentials:
cat > .env << 'EOL'
DB_HOST=your-project.pooler.supabase.com
DB_NAME=postgres
DB_USER=postgres.your_project_ref
DB_PASSWORD=your_password
DB_PORT=6543
EOL

# Initialize database
python src/database/load_data.py

# Run application
streamlit run src/app/Home.py
```

## 📈 Key Results (Example from 8 Weeks of Data)

| Metric | Value |
|--------|-------|
| **Total Tracked Products** | 32 |
| **Total Purchases Logged** | 94 |
| **Average Weekly Spend** | £22.15 |
| **Total Waste Cost** | £18.73 (8.4% of total spend) |
| **Fresh Produce Waste Rate** | 35% |
| **Forecast Accuracy** | 87% (MAE < 13%) |
| **High Waste Risk Items Identified** | 5 |

### Key Insights Discovered

1. **Fresh Produce has highest waste** (35% avg) → Recommendation: Buy smaller packs more frequently
2. **Clubcard prices save £3.20/week on average** → Use Clubcard strategically
3. **Optimal shopping frequency: Every 4-5 days** → Reduces waste vs. weekly shopping
4. **Bakery items waste 20%** → Freeze half immediately after purchase

## 🎓 Learning Outcomes

This project demonstrates:

### Technical Skills
- **Database Design:** Proper relational schema with foreign keys, indexes, and views
- **SQL Proficiency:** Window functions, CTEs, aggregations, date arithmetic
- **Python:** Pandas for data manipulation, matplotlib/seaborn for visualization
- **ML/Forecasting:** Exponential smoothing, time series analysis
- **Web Development:** Streamlit for interactive dashboards
- **Cloud Deployment:** Streamlit Cloud with secrets management

### Business/Analytical Skills
- **Retail Analytics:** Price intelligence, promotional analysis
- **Supply Chain:** EOQ modeling, inventory optimization
- **Data-Driven Decision Making:** Using forecasts to inform purchasing
- **Problem Framing:** Identifying underserved market segment

### Software Engineering
- **Git/Version Control:** Feature branches, commit messages
- **Environment Management:** Virtual environments, requirements.txt
- **Code Organization:** Modular architecture, separation of concerns
- **Documentation:** Clear README, inline comments

## 🔮 Future Enhancements

- [ ] Automated price scraping with GitHub Actions (weekly schedule)
- [ ] Receipt OCR for faster purchase logging
- [ ] Multi-user support for household sharing
- [ ] Mobile app (React Native wrapper)
- [ ] Integration with Tesco/Sainsbury's APIs (if available)
- [ ] Advanced forecasting (Prophet, ARIMA)
- [ ] Carbon footprint tracking
- [ ] Meal planning integration

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**[Your Name]**
- Portfolio: [yourportfolio.com]
- LinkedIn: [linkedin.com/in/yourprofile]
- Email: your.email@example.com

---

**Built as a portfolio project demonstrating end-to-end data analytics and engineering skills**

*Started: April 2026 | Status: Active Development*
