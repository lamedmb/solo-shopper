"""
Solo Shopper - Mobile Home
Quick access to all logging features
"""

import streamlit as st

st.set_page_config(
    page_title="Solo Shopper",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 Solo Shopper")
st.markdown("### Quick Actions")

st.markdown("""
Welcome to Solo Shopper! Use the sidebar to navigate between:
- 🛒 **Log Purchase** - Add grocery items you bought
- 🗑️ **Log Waste** - Track weekly consumption & waste
- 📊 **Dashboard** - View your analytics

👈 Open the sidebar to get started!
""")

st.markdown("---")

# Quick stats on home page
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db_connection import execute_query

col1, col2, col3 = st.columns(3)

with col1:
    total_products = execute_query("SELECT COUNT(*) as count FROM products")[0]['count']
    st.metric("Products", total_products)

with col2:
    total_purchases = execute_query("SELECT COUNT(*) as count FROM purchases")[0]['count']
    st.metric("Purchases", total_purchases)

with col3:
    week_purchases = execute_query("""
        SELECT COUNT(*) as count FROM purchases 
        WHERE date >= CURRENT_DATE - INTERVAL '7 days'
    """)[0]['count']
    st.metric("This Week", week_purchases)

st.markdown("---")
st.caption("Solo Shopper - Personal Grocery Intelligence")