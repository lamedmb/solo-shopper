"""
Solo Shopper - Mobile Home
Quick access to all logging features
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db_connection import execute_query

st.set_page_config(
    page_title="Solo Shopper",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 Solo Shopper")
st.markdown("### Quick Actions")

st.markdown("""
Welcome to Solo Shopper! Choose an action below or use the sidebar to navigate.
""")

# Quick action buttons that work on mobile
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛒 Log Purchase")
    st.markdown("Add grocery items you bought")
    # No actual button - just tell them to use sidebar
    st.info("👈 Open sidebar and select 'log_purchase'")

with col2:
    st.markdown("### 🗑️ Log Waste")
    st.markdown("Track weekly consumption")
    st.info("👈 Open sidebar and select 'log_waste'")

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.markdown("### ➕ Add Product")
    st.markdown("Add new products")
    st.info("👈 Open sidebar and select 'add_product'")

with col4:
    st.markdown("### 📊 Dashboard")
    st.markdown("View your analytics")
    st.info("👈 Open sidebar and select 'dashboard'")

st.markdown("---")

# Quick stats
st.markdown("### 📈 Quick Stats")

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