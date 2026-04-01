"""
Solo Shopper - Personal Grocery Intelligence Dashboard
Main Streamlit application
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Fix import path for Streamlit multi-page app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.db_connection import execute_query

# Page config
st.set_page_config(
    page_title="Solo Shopper Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🛒 Solo Shopper Dashboard</p>', unsafe_allow_html=True)
st.markdown("*Personal Grocery Intelligence System*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 🛒 Solo Shopper")
    st.markdown("Personal Grocery Intelligence")
    st.markdown("---")
    
    st.markdown("### Navigation")
    st.markdown("Use the tabs above to explore your grocery data")
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    
    # Get total products
    total_products = execute_query("SELECT COUNT(*) as count FROM products")[0]['count']
    total_purchases = execute_query("SELECT COUNT(*) as count FROM purchases")[0]['count']
    
    st.metric("Products Tracked", total_products)
    st.metric("Total Purchases", total_purchases)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💰 Price Tracker", "🗑️ Waste Log", "📝 Shopping List"])

# TAB 1: DASHBOARD
with tab1:
    st.header("Weekly Summary")
    
    col1, col2, col3 = st.columns(3)
    
    # Get latest week's data
    latest_week_query = """
    SELECT 
        date,
        SUM(price_paid) as total_spent,
        COUNT(*) as items_bought
    FROM purchases
    GROUP BY date
    ORDER BY date DESC
    LIMIT 1
    """
    latest_week = execute_query(latest_week_query)
    
    if latest_week:
        week_data = latest_week[0]
        
        # Get waste for that week
        waste_query = """
        SELECT SUM(waste_cost_gbp) as total_waste
        FROM consumption_log
        WHERE week_ending = %s
        """
        waste_data = execute_query(waste_query, (week_data['date'],))
        total_waste = waste_data[0]['total_waste'] if waste_data[0]['total_waste'] else 0
        
        with col1:
            st.metric("💸 Total Spent", f"£{week_data['total_spent']:.2f}")
        
        with col2:
            st.metric("🗑️ Total Wasted", f"£{total_waste:.2f}")
        
        with col3:
            effective_cost = week_data['total_spent'] - total_waste
            st.metric("✅ Effective Cost", f"£{effective_cost:.2f}")
    
    st.markdown("---")
    
    # Spending over time
    st.subheader("Spending Trend")
    
    spending_trend_query = """
    SELECT 
        date,
        SUM(price_paid) as total_spent
    FROM purchases
    GROUP BY date
    ORDER BY date
    """
    spending_data = pd.DataFrame(execute_query(spending_trend_query))
    
    if not spending_data.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(spending_data['date'], spending_data['total_spent'], marker='o', linewidth=2, color='#1f77b4')
        ax.set_xlabel('Date')
        ax.set_ylabel('Total Spent (£)')
        ax.set_title('Weekly Spending')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        st.info("No spending data available yet")
    
    # Store comparison
    st.subheader("Store Comparison")
    
    store_comparison_query = """
    SELECT 
        store,
        COUNT(*) as purchases,
        SUM(price_paid) as total_spent,
        AVG(price_paid) as avg_price
    FROM purchases
    GROUP BY store
    ORDER BY total_spent DESC
    """
    store_data = pd.DataFrame(execute_query(store_comparison_query))
    
    if not store_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(store_data)]
            ax.bar(store_data['store'], store_data['total_spent'], color=colors)
            ax.set_ylabel('Total Spent (£)')
            ax.set_title('Total Spending by Store')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.dataframe(store_data, use_container_width=True)

# TAB 2: PRICE TRACKER
with tab2:
    st.header("Price Intelligence")
    
    # Get latest prices
    latest_prices_query = """
    SELECT 
        product_name,
        store,
        regular_price,
        promotional_price,
        promotion_type,
        price_date
    FROM latest_prices
    ORDER BY product_name, store
    """
    prices_df = pd.DataFrame(execute_query(latest_prices_query))
    
    if not prices_df.empty:
        # Filter by product
        products = sorted(prices_df['product_name'].unique())
        selected_product = st.selectbox("Select a product to compare:", products)
        
        product_prices = prices_df[prices_df['product_name'] == selected_product]
        
        st.subheader(f"Price Comparison: {selected_product}")
        
        # Display comparison
        col1, col2 = st.columns(2)
        
        for idx, row in product_prices.iterrows():
            col = col1 if idx % 2 == 0 else col2
            
            with col:
                with st.container():
                    st.markdown(f"### {row['store']}")
                    
                    if pd.notna(row['promotional_price']):
                        st.markdown(f"~~£{row['regular_price']:.2f}~~ **£{row['promotional_price']:.2f}**")
                        st.markdown(f"*{row['promotion_type']}*")
                        savings = row['regular_price'] - row['promotional_price']
                        st.success(f"Save £{savings:.2f}")
                    else:
                        st.markdown(f"**£{row['regular_price']:.2f}**")
                    
                    st.caption(f"Updated: {row['price_date']}")
        
        st.markdown("---")
        
        # All prices table
        st.subheader("All Current Prices")
        st.dataframe(prices_df, use_container_width=True)
    else:
        st.info("No price data available")

# TAB 3: WASTE LOG
with tab3:
    st.header("Consumption & Waste Analysis")
    
    # Waste by category
    waste_by_category_query = """
    SELECT * FROM waste_by_category
    """
    waste_df = pd.DataFrame(execute_query(waste_by_category_query))
    
    if not waste_df.empty:
        # Convert Decimal columns to float
        waste_df['avg_waste_rate'] = waste_df['avg_waste_rate'].astype(float)
        waste_df['total_waste_cost'] = waste_df['total_waste_cost'].astype(float)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Waste by Category")
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(waste_df['category'], waste_df['total_waste_cost'], color='#ff7f0e')
            ax.set_xlabel('Total Waste Cost (£)')
            ax.set_title('Which Categories Cost You Most in Waste?')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.subheader("Average Waste Rate")
            fig, ax = plt.subplots(figsize=(8, 6))
            # Convert to numpy array of floats
            waste_rates = waste_df['avg_waste_rate'].values.astype(float)
            
            # Normalize to 0-1 range for colormap
            if len(waste_rates) > 1 and waste_rates.max() > waste_rates.min():
                norm_rates = (waste_rates - waste_rates.min()) / (waste_rates.max() - waste_rates.min())
            else:
                norm_rates = waste_rates / (waste_rates.max() + 0.001)
            
            colors = plt.cm.RdYlGn_r(norm_rates)
            
            ax.barh(waste_df['category'], waste_rates, color=colors)
            ax.set_xlabel('Average Waste Rate (0-1)')
            ax.set_title('Proportion Wasted by Category')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        st.dataframe(waste_df, use_container_width=True)
        
        # Total waste summary
        total_waste_cost = float(waste_df['total_waste_cost'].sum())
        st.error(f"💸 **Total money wasted: £{total_waste_cost:.2f}**")
    else:
        st.info("No waste data available")

# TAB 4: SHOPPING LIST
with tab4:
    st.header("Smart Shopping List")
    
    st.info("🚧 Shopping list generation coming in Phase 6 (Forecasting Module)")
    
    # Show most frequently bought items for now
    frequent_items_query = """
    SELECT 
        p.name,
        COUNT(*) as purchase_count,
        AVG(pur.price_paid) as avg_price,
        MIN(pur.date) as first_bought,
        MAX(pur.date) as last_bought
    FROM purchases pur
    JOIN products p ON pur.product_id = p.product_id
    GROUP BY p.name
    ORDER BY purchase_count DESC
    LIMIT 10
    """
    frequent_df = pd.DataFrame(execute_query(frequent_items_query))
    
    if not frequent_df.empty:
        st.subheader("Your Most Frequently Bought Items")
        st.dataframe(frequent_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*Solo Shopper - Built with Streamlit | Data stored in Supabase PostgreSQL*")