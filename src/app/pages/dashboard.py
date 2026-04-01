"""
Solo Shopper - Enhanced Dashboard
Interactive analytics with filters and insights
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, date
import sys
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.db_connection import execute_query

# Page config
st.set_page_config(
    page_title="Solo Shopper Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS
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
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🛒 Solo Shopper Dashboard</p>', unsafe_allow_html=True)
st.markdown("*Personal Grocery Intelligence System*")

# Sidebar filters
with st.sidebar:
    st.markdown("### 📊 Filters")
    
    # Date range filter
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 3 months", "All time"]
    )
    
    # Map to SQL
    if date_range == "Last 7 days":
        date_filter = "WHERE p.date >= CURRENT_DATE - INTERVAL '7 days'"
    elif date_range == "Last 30 days":
        date_filter = "WHERE p.date >= CURRENT_DATE - INTERVAL '30 days'"
    elif date_range == "Last 3 months":
        date_filter = "WHERE p.date >= CURRENT_DATE - INTERVAL '3 months'"
    else:
        date_filter = ""
    
    # Store filter
    store_filter = st.multiselect(
        "Store",
        ["Tesco", "Sainsburys"],
        default=["Tesco", "Sainsburys"]
    )
    
    st.markdown("---")
    
    # Quick stats
    total_products = execute_query("SELECT COUNT(*) as count FROM products")[0]['count']
    total_purchases = execute_query("SELECT COUNT(*) as count FROM purchases")[0]['count']
    
    st.metric("Products Tracked", total_products)
    st.metric("Total Purchases", total_purchases)

st.markdown("---")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "💰 Spending Analysis", 
    "🗑️ Waste Insights", 
    "⚠️ Expiring Soon",
    "📝 Shopping List"
])

# TAB 1: OVERVIEW
with tab1:
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Total spent
    spent_query = f"""
    SELECT SUM(price_paid) as total 
    FROM purchases p
    {date_filter}
    """
    total_spent = execute_query(spent_query)[0]['total']
    total_spent = float(total_spent) if total_spent else 0
    
    with col1:
        st.metric("💸 Total Spent", f"£{total_spent:.2f}")
    
    # Total wasted
    waste_query = f"""
    SELECT SUM(waste_cost_gbp) as total
    FROM consumption_log cl
    JOIN purchases p ON cl.purchase_id = p.purchase_id
    {date_filter.replace('p.date', 'cl.week_ending')}
    """
    total_waste = execute_query(waste_query)[0]['total']
    total_waste = float(total_waste) if total_waste else 0
    
    with col2:
        st.metric("🗑️ Total Wasted", f"£{total_waste:.2f}")
    
    # Effective cost
    with col3:
        effective = total_spent - total_waste
        st.metric("✅ Effective Cost", f"£{effective:.2f}")
    
    # Waste rate
    with col4:
        waste_pct = (total_waste / total_spent * 100) if total_spent > 0 else 0
        st.metric("📊 Waste Rate", f"{waste_pct:.1f}%")
    
    st.markdown("---")
    
    # Spending trend over time
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Spending Trend")
        
        trend_query = f"""
        SELECT 
            date,
            SUM(price_paid) as spent
        FROM purchases p
        {date_filter}
        GROUP BY date
        ORDER BY date
        """
        trend_data = pd.DataFrame(execute_query(trend_query))
        
        if not trend_data.empty:
            trend_data['spent'] = trend_data['spent'].astype(float)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(trend_data['date'], trend_data['spent'], marker='o', linewidth=2, color='#1f77b4')
            ax.fill_between(trend_data['date'], trend_data['spent'], alpha=0.3, color='#1f77b4')
            ax.set_xlabel('Date')
            ax.set_ylabel('Spent (£)')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No spending data for selected period")
    
    with col2:
        st.subheader("Category Breakdown")
        
        category_query = f"""
        SELECT 
            prod.category,
            SUM(p.price_paid) as total
        FROM purchases p
        JOIN products prod ON p.product_id = prod.product_id
        {date_filter}
        GROUP BY prod.category
        ORDER BY total DESC
        """
        category_data = pd.DataFrame(execute_query(category_query))
        
        if not category_data.empty:
            category_data['total'] = category_data['total'].astype(float)
            
            fig, ax = plt.subplots(figsize=(6, 6))
            colors = plt.cm.Set3(range(len(category_data)))
            ax.pie(category_data['total'], labels=category_data['category'], autopct='%1.1f%%', colors=colors)
            ax.set_title('Spending by Category')
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No category data for selected period")

# TAB 2: SPENDING ANALYSIS
with tab2:
    st.header("💰 Spending Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Most Expensive Items")
        
        expensive_query = f"""
        SELECT 
            prod.name,
            COUNT(*) as times_bought,
            AVG(p.price_paid) as avg_price,
            SUM(p.price_paid) as total_spent
        FROM purchases p
        JOIN products prod ON p.product_id = prod.product_id
        {date_filter}
        GROUP BY prod.name
        ORDER BY total_spent DESC
        LIMIT 10
        """
        expensive_df = pd.DataFrame(execute_query(expensive_query))
        
        if not expensive_df.empty:
            expensive_df['total_spent'] = expensive_df['total_spent'].astype(float)
            expensive_df['avg_price'] = expensive_df['avg_price'].astype(float)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(expensive_df['name'], expensive_df['total_spent'], color='#ff7f0e')
            ax.set_xlabel('Total Spent (£)')
            ax.set_title('Your Biggest Expenses')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            st.dataframe(expensive_df, use_container_width=True, hide_index=True)
        else:
            st.info("No purchase data for selected period")
    
    with col2:
        st.subheader("Store Comparison")
        
        store_comparison_query = f"""
        SELECT 
            store,
            COUNT(*) as purchases,
            SUM(price_paid) as total_spent,
            AVG(price_paid) as avg_per_item
        FROM purchases p
        {date_filter}
        GROUP BY store
        """
        store_data = pd.DataFrame(execute_query(store_comparison_query))
        
        if not store_data.empty:
            store_data['total_spent'] = store_data['total_spent'].astype(float)
            store_data['avg_per_item'] = store_data['avg_per_item'].astype(float)
            
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = ['#1f77b4', '#ff7f0e']
            ax.bar(store_data['store'], store_data['total_spent'], color=colors)
            ax.set_ylabel('Total Spent (£)')
            ax.set_title('Total Spending by Store')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            st.dataframe(store_data, use_container_width=True, hide_index=True)
        else:
            st.info("No store data for selected period")
    
    st.markdown("---")
    
    # Promotional price analysis
    st.subheader("Promotional Price Usage")
    
    promo_query = f"""
    SELECT 
        promotional_price_used,
        COUNT(*) as count,
        SUM(price_paid) as total_spent
    FROM purchases p
    {date_filter}
    GROUP BY promotional_price_used
    """
    promo_data = pd.DataFrame(execute_query(promo_query))
    
    if not promo_data.empty:
        promo_data['promotional_price_used'] = promo_data['promotional_price_used'].map({
            True: 'Clubcard/Nectar', 
            False: 'Regular Price'
        })
        promo_data['total_spent'] = promo_data['total_spent'].astype(float)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(promo_data['promotional_price_used'], promo_data['count'], color=['#2ca02c', '#d62728'])
            ax.set_ylabel('Number of Items')
            ax.set_title('Promotional vs Regular Purchases')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.dataframe(promo_data, use_container_width=True, hide_index=True)

# TAB 3: WASTE INSIGHTS
with tab3:
    st.header("🗑️ Waste Insights")
    
    waste_by_category_query = """
    SELECT * FROM waste_by_category
    """
    waste_df = pd.DataFrame(execute_query(waste_by_category_query))
    
    if not waste_df.empty:
        waste_df['avg_waste_rate'] = waste_df['avg_waste_rate'].astype(float)
        waste_df['total_waste_cost'] = waste_df['total_waste_cost'].astype(float)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Waste Cost by Category")
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(waste_df['category'], waste_df['total_waste_cost'], color='#d62728')
            ax.set_xlabel('Waste Cost (£)')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.subheader("Waste Rate by Category")
            fig, ax = plt.subplots(figsize=(8, 6))
            waste_rates = waste_df['avg_waste_rate'].values
            # Normalize for color mapping
            if len(waste_rates) > 1 and waste_rates.max() > waste_rates.min():
                norm_rates = (waste_rates - waste_rates.min()) / (waste_rates.max() - waste_rates.min())
            else:
                norm_rates = waste_rates / (waste_rates.max() + 0.001)
            colors = plt.cm.RdYlGn_r(norm_rates)
            ax.barh(waste_df['category'], waste_rates * 100, color=colors)
            ax.set_xlabel('Waste Rate (%)')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        st.dataframe(waste_df, use_container_width=True, hide_index=True)
        
        # Total waste summary
        total_waste_cost = waste_df['total_waste_cost'].sum()
        st.error(f"💸 **Total money wasted: £{total_waste_cost:.2f}**")
        
        # Waste reasons breakdown
        st.markdown("---")
        st.subheader("Why Are You Wasting?")
        
        reasons_query = """
        SELECT 
            waste_reason,
            COUNT(*) as count,
            SUM(waste_cost_gbp) as cost
        FROM consumption_log
        WHERE waste_reason IS NOT NULL
        GROUP BY waste_reason
        ORDER BY cost DESC
        """
        reasons_df = pd.DataFrame(execute_query(reasons_query))
        
        if not reasons_df.empty:
            reasons_df['cost'] = reasons_df['cost'].astype(float)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(reasons_df['waste_reason'], reasons_df['cost'], color='#ff7f0e')
            ax.set_xlabel('Reason')
            ax.set_ylabel('Total Cost (£)')
            ax.set_title('Waste Cost by Reason')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            st.dataframe(reasons_df, use_container_width=True, hide_index=True)
    else:
        st.info("No waste data available yet. Start logging your weekly consumption!")

# TAB 4: EXPIRING SOON
with tab4:
    st.header("⚠️ Items Expiring Soon")
    
    # Check if expiry_date column exists
    try:
        expiring_query = """
        SELECT 
            product_name,
            purchase_date,
            expiry_date,
            days_until_expiry,
            price_paid
        FROM expiring_soon
        ORDER BY days_until_expiry
        """
        
        expiring_df = pd.DataFrame(execute_query(expiring_query))
        
        if not expiring_df.empty:
            expiring_df['price_paid'] = expiring_df['price_paid'].astype(float)
            
            # Group by urgency
            today = expiring_df[expiring_df['days_until_expiry'] == 0]
            tomorrow = expiring_df[expiring_df['days_until_expiry'] == 1]
            this_week = expiring_df[(expiring_df['days_until_expiry'] > 1) & (expiring_df['days_until_expiry'] <= 7)]
            
            if not today.empty:
                st.error(f"🚨 **{len(today)} items expire TODAY!**")
                st.dataframe(today, use_container_width=True, hide_index=True)
                st.markdown("---")
            
            if not tomorrow.empty:
                st.warning(f"⚠️ **{len(tomorrow)} items expire tomorrow**")
                st.dataframe(tomorrow, use_container_width=True, hide_index=True)
                st.markdown("---")
            
            if not this_week.empty:
                st.info(f"📅 **{len(this_week)} items expire this week**")
                st.dataframe(this_week, use_container_width=True, hide_index=True)
            
            # Priority consumption list
            st.markdown("---")
            st.subheader("🎯 Priority Consumption Order")
            st.markdown("Eat these items first to minimize waste:")
            
            priority_list = expiring_df.head(10)
            for idx, item in priority_list.iterrows():
                days = item['days_until_expiry']
                if days == 0:
                    st.error(f"**Priority {idx+1}:** {item['product_name']} - Expires TODAY!")
                elif days == 1:
                    st.warning(f"**Priority {idx+1}:** {item['product_name']} - Expires tomorrow")
                else:
                    st.info(f"**Priority {idx+1}:** {item['product_name']} - Expires in {days} days")
        else:
            st.success("✅ No items expiring soon!")
    
    except Exception as e:
        st.warning("⚠️ Expiry tracking not available yet. Add the expiry_date column to your purchases to use this feature!")
        st.caption(f"Error: {e}")

# TAB 5: SHOPPING LIST  
with tab5:
    st.header("📝 Smart Shopping List")
    st.markdown("AI-generated recommendations based on your consumption patterns")
    
    try:
        # Import forecasting modules
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from forecasting.eoq_optimizer import generate_shopping_list_recommendations
        
        if st.button("🔮 Generate This Week's List", type="primary"):
            with st.spinner("Analyzing your consumption patterns..."):
                recommendations = generate_shopping_list_recommendations()
            
            if recommendations:
                st.success(f"✅ Generated {len(recommendations)} recommendations")
                
                # Group by purchase frequency
                buy_now = [r for r in recommendations if r.get('purchase_frequency_weeks') == 1]
                buy_soon = [r for r in recommendations if r.get('purchase_frequency_weeks', 99) in [2, 3]]
                high_waste_risk = [r for r in recommendations if r.get('waste_risk') == 'HIGH']
                
                # Buy This Week
                if buy_now:
                    st.subheader("🛒 Buy This Week")
                    buy_df = pd.DataFrame(buy_now)
                    st.dataframe(
                        buy_df[['product_name', 'recommendation', 'cost_per_week', 'waste_risk']],
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Buy Soon
                if buy_soon:
                    st.subheader("⏰ Buy in Next 2-3 Weeks")
                    soon_df = pd.DataFrame(buy_soon)
                    st.dataframe(
                        soon_df[['product_name', 'recommendation', 'waste_risk']],
                        use_container_width=True,
                        hide_index=True
                    )
                
                # High Waste Risk Items
                if high_waste_risk:
                    st.subheader("🚨 High Waste Risk - Consider Smaller Packs")
                    risk_df = pd.DataFrame(high_waste_risk)
                    st.dataframe(
                        risk_df[['product_name', 'recommendation']],
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("Not enough consumption data yet. Log waste for 3+ weeks to generate recommendations.")
    
    except Exception as e:
        st.error(f"Error generating shopping list: {e}")
        st.info("Make sure you've logged consumption data for at least 3 weeks")

st.markdown("---")
st.caption("*Solo Shopper - Built with Streamlit | Data stored in Supabase PostgreSQL*")