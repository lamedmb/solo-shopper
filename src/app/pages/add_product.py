"""
Solo Shopper - Add New Product
Quickly add new products to your database
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database.db_connection import execute_query, get_connection

st.set_page_config(
    page_title="Add Product",
    page_icon="➕",
    layout="centered"
)

st.title("➕ Add New Product")
st.markdown("Add products that aren't in your list yet")

# Add product form
with st.form("add_product_form", clear_on_submit=True):
    st.subheader("Product Details")
    
    product_name = st.text_input(
        "Product Name",
        placeholder="e.g., Avocados 4pk, Orange Juice 1L, Shampoo 500ml"
    )
    
    # UPDATED CATEGORIES
    category = st.selectbox(
        "Category",
        [
            "Vegetables",
            "Meat & Fish",
            "Dairy & Eggs",
            "Bakery",
            "Carbs & Grains",
            "Frozen",
            "Ready-made Meals",
            "Spices & Condiments",
            "Desserts & Snacks",
            "Drinks",
            "Household Essentials",
            "Other"
        ]
    )
    
    shelf_life = st.number_input(
        "Typical Shelf Life (days)",
        min_value=1,
        max_value=730,
        value=7,
        help="How many days does this typically last?"
    )
    
    submitted = st.form_submit_button("➕ Add Product", use_container_width=True)
    
    if submitted:
        if not product_name:
            st.error("❌ Please enter a product name")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                
                cur.execute("""
                    INSERT INTO products (name, category, typical_shelf_life_days)
                    VALUES (%s, %s, %s)
                    RETURNING product_id
                """, (product_name, category, shelf_life))
                
                product_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"✅ Added: {product_name} (ID: {product_id})")
                st.info("💡 You can now select this product when logging purchases!")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")

# Show all products
st.subheader("Current Products")

all_products_query = """
SELECT name, category, typical_shelf_life_days 
FROM products 
ORDER BY category, name
"""

all_products = pd.DataFrame(execute_query(all_products_query))

if not all_products.empty:
    all_products.columns = ['Product', 'Category', 'Shelf Life (days)']
    
    # Filter by category
    category_filter = st.selectbox(
        "Filter by category:",
        ["All"] + sorted(all_products['Category'].unique())
    )
    
    if category_filter != "All":
        filtered = all_products[all_products['Category'] == category_filter]
    else:
        filtered = all_products
    
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=400)
    st.caption(f"Showing {len(filtered)} of {len(all_products)} products")