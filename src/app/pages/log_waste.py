"""
Solo Shopper - Weekly Waste Logger
Log what you consumed vs. wasted each week
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# Fix import path for Streamlit multi-page app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.db_connection import execute_query, get_connection

# Page config
st.set_page_config(
    page_title="Log Waste",
    page_icon="🗑️",
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

st.title("🗑️ Log Weekly Waste")
st.markdown("Track what you consumed vs. wasted")

# Select week to log
st.subheader("Which week are you logging?")

week_ending = st.date_input(
    "Week ending (usually Sunday)",
    value=date.today(),
    max_value=date.today()
)

# Get purchases from that week
purchases_query = """
SELECT 
    p.purchase_id,
    p.date,
    prod.name,
    p.store,
    p.price_paid
FROM purchases p
JOIN products prod ON p.product_id = prod.product_id
WHERE p.date >= %s - INTERVAL '7 days'
  AND p.date <= %s
  AND NOT EXISTS (
      SELECT 1 FROM consumption_log cl 
      WHERE cl.purchase_id = p.purchase_id 
      AND cl.week_ending = %s
  )
ORDER BY p.date DESC, prod.name
"""

purchases = execute_query(purchases_query, (week_ending, week_ending, week_ending))

if not purchases:
    st.info(f"No unlogged purchases for week ending {week_ending}")
    st.markdown("Either you haven't shopped this week, or you've already logged everything!")
else:
    st.success(f"Found {len(purchases)} items to log")
    
    # Form for each purchase
    with st.form("waste_form"):
        logged_items = []
        
        for idx, purchase in enumerate(purchases):
            st.markdown("---")
            st.markdown(f"**{purchase['name']}** - £{float(purchase['price_paid']):.2f}")
            st.caption(f"Bought on {purchase['date']} from {purchase['store']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                consumed = st.slider(
                    "Consumed %",
                    0, 100, 70,
                    key=f"consumed_{idx}",
                    help="What % did you actually use?"
                )
            
            with col2:
                wasted = 100 - consumed
                st.metric("Wasted %", f"{wasted}%")
            
            with col3:
                # FIXED: Convert Decimal to float
                waste_cost = (wasted / 100) * float(purchase['price_paid'])
                st.metric("£ Wasted", f"£{waste_cost:.2f}")
            
            # Waste reason if significant waste
            if wasted > 10:
                reason = st.selectbox(
                    "Why wasted?",
                    ["Expired before use", "Over-bought", "Didn't cook as planned", "Went bad", "Other"],
                    key=f"reason_{idx}"
                )
            else:
                reason = None
            
            logged_items.append({
                'purchase_id': purchase['purchase_id'],
                'consumed': consumed / 100,
                'wasted': wasted / 100,
                'reason': reason,
                'waste_cost': waste_cost
            })
        
        # FIXED: Added the submit button!
        submitted = st.form_submit_button("💾 Save All Waste Logs", use_container_width=True)
        
        if submitted:
            try:
                conn = get_connection()
                cur = conn.cursor()
                
                insert_query = """
                INSERT INTO consumption_log 
                (purchase_id, week_ending, proportion_consumed, proportion_wasted, waste_reason, waste_cost_gbp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                for item in logged_items:
                    cur.execute(insert_query, (
                        item['purchase_id'],
                        week_ending,
                        item['consumed'],
                        item['wasted'],
                        item['reason'],
                        item['waste_cost']
                    ))
                
                conn.commit()
                cur.close()
                conn.close()
                
                total_wasted = sum(item['waste_cost'] for item in logged_items)
                
                st.success(f"✅ Saved {len(logged_items)} items!")
                st.error(f"💸 Total wasted this week: £{total_wasted:.2f}")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")

# Show waste summary
st.subheader("Your Waste Summary")

waste_summary_query = """
SELECT 
    COUNT(*) as items_logged,
    ROUND(AVG(proportion_wasted), 2) as avg_waste_rate,
    SUM(waste_cost_gbp) as total_waste
FROM consumption_log
WHERE week_ending >= CURRENT_DATE - INTERVAL '30 days'
"""

summary = execute_query(waste_summary_query)[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Items Logged (30d)", summary['items_logged'] or 0)

with col2:
    avg_waste = float(summary['avg_waste_rate'] or 0) * 100
    st.metric("Avg Waste Rate", f"{avg_waste:.0f}%")

with col3:
    total_waste = float(summary['total_waste'] or 0)
    st.metric("Total Wasted (30d)", f"£{total_waste:.2f}")