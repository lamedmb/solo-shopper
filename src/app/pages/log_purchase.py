"""
Solo Shopper - Mobile Purchase Logger
Quick data entry form for logging grocery purchases on the go
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
from pathlib import Path

# Fix import path for Streamlit multi-page app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.db_connection import execute_query, get_connection

# Page config
st.set_page_config(
    page_title="Log Purchase",
    page_icon="🛒",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛒 Log Purchase")
st.markdown("Quick grocery logging")

# Get list of products for dropdown
products_query = "SELECT product_id, name FROM products ORDER BY name"
products = execute_query(products_query)
product_dict = {p['name']: p['product_id'] for p in products}

# Purchase logging form
with st.form("purchase_form", clear_on_submit=True):
    st.subheader("Purchase Details")
    
    # Date
    purchase_date = st.date_input(
        "Date",
        value=date.today(),
        max_value=date.today()
    )
    
    # Store
    store = st.radio(
        "Store",
        ["Tesco", "Sainsburys"],
        horizontal=True
    )
    
    # Product selection
    selected_product = st.selectbox(
        "Product",
        options=list(product_dict.keys()),
        help="Can't find your product? Add it in the 'Add Product' page first"
    )
    
    # Price
    col1, col2 = st.columns(2)
    with col1:
        price_paid = st.number_input(
            "Price Paid (£)",
            min_value=0.01,
            max_value=100.00,
            value=1.00,
            step=0.01,
            format="%.2f"
        )
    
    with col2:
        clubcard_used = st.checkbox("Clubcard/Nectar Price?")
    
    # Submit button
    submitted = st.form_submit_button("💾 Save Purchase", use_container_width=True)
    
    if submitted:
        try:
            product_id = product_dict[selected_product]
            
            # Insert into database
            conn = get_connection()
            cur = conn.cursor()
            
            # FIXED: Don't specify purchase_id - it auto-generates
            insert_query = """
            INSERT INTO purchases (date, product_id, store, price_paid, promotional_price_used)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING purchase_id
            """
            
            cur.execute(insert_query, (
                purchase_date,
                product_id,
                store,
                price_paid,
                clubcard_used
            ))
            
            purchase_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            st.success(f"✅ Saved! {selected_product} - £{price_paid:.2f}")
            
        except Exception as e:
            st.error(f"❌ Error saving: {e}")

st.markdown("---")

# Recent purchases preview
st.subheader("Recent Purchases (Last 5)")

recent_query = """
SELECT 
    p.date,
    prod.name,
    p.store,
    p.price_paid,
    p.promotional_price_used
FROM purchases p
JOIN products prod ON p.product_id = prod.product_id
ORDER BY p.created_at DESC
LIMIT 5
"""

recent = pd.DataFrame(execute_query(recent_query))

if not recent.empty:
    recent['promotional_price_used'] = recent['promotional_price_used'].map({True: '✓', False: ''})
    recent.columns = ['Date', 'Product', 'Store', 'Price', 'Promo']
    st.dataframe(recent, use_container_width=True, hide_index=True)
else:
    st.info("No purchases logged yet")

# Quick stats
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    total_count = execute_query("SELECT COUNT(*) as count FROM purchases")[0]['count']
    st.metric("Total Logged", total_count)

with col2:
    this_week = execute_query("""
        SELECT COUNT(*) as count FROM purchases 
        WHERE date >= CURRENT_DATE - INTERVAL '7 days'
    """)[0]['count']
    st.metric("This Week", this_week)