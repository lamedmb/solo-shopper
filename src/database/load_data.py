"""Load synthetic CSV data into PostgreSQL"""

import pandas as pd
from pathlib import Path
from db_connection import get_connection, execute_script

DATA_DIR = Path("data/raw")

def load_all_data():
    """Load all CSV files into database"""
    
    # First, create the schema
    print("📋 Creating database schema...")
    execute_script("src/database/schema.sql")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Load products
        print("📦 Loading products...")
        products = pd.read_csv(DATA_DIR / 'products.csv')
        for _, row in products.iterrows():
            cur.execute("""
                INSERT INTO products (product_id, name, category, typical_shelf_life_days, base_price_gbp)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING
            """, (row['product_id'], row['name'], row['category'], 
                  row['typical_shelf_life_days'], row['base_price_gbp']))
        
        # 2. Load price history
        print("💰 Loading price history...")
        prices = pd.read_csv(DATA_DIR / 'price_history.csv')
        for _, row in prices.iterrows():
            cur.execute("""
                INSERT INTO price_history (date, product_id, store, regular_price, promotional_price, promotion_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, product_id, store) DO NOTHING
            """, (row['date'], row['product_id'], row['store'], row['regular_price'],
                  row['promotional_price'] if pd.notna(row['promotional_price']) else None,
                  row['promotion_type'] if pd.notna(row['promotion_type']) else None))
        
        # 3. Load purchases
        print("🧾 Loading purchases...")
        purchases = pd.read_csv(DATA_DIR / 'purchases.csv')
        for _, row in purchases.iterrows():
            cur.execute("""
                INSERT INTO purchases (purchase_id, date, product_id, store, price_paid, promotional_price_used)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['purchase_id'], row['date'], row['product_id'], 
                  row['store'], row['price_paid'], row['promotional_price_used']))
        
        # 4. Load consumption log
        print("📊 Loading consumption log...")
        consumption = pd.read_csv(DATA_DIR / 'consumption_log.csv')
        for _, row in consumption.iterrows():
            cur.execute("""
                INSERT INTO consumption_log (purchase_id, week_ending, proportion_consumed, 
                                            proportion_wasted, waste_reason, waste_cost_gbp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['purchase_id'], row['week_ending'], row['proportion_consumed'],
                  row['proportion_wasted'], 
                  row['waste_reason'] if pd.notna(row['waste_reason']) else None,
                  row['waste_cost_gbp']))
        
        # 5. FIX SEQUENCES (NEW - prevents duplicate key errors)
        print("\n🔧 Fixing sequences...")
        cur.execute("""
            SELECT setval('products_product_id_seq', 
                         (SELECT MAX(product_id) FROM products));
        """)
        cur.execute("""
            SELECT setval('purchases_purchase_id_seq', 
                         (SELECT MAX(purchase_id) FROM purchases));
        """)
        print("✅ Sequences fixed!")
        
        conn.commit()
        print("\n✅ All data loaded successfully!")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM products")
        print(f"   Products: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM price_history")
        print(f"   Price records: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM purchases")
        print(f"   Purchases: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM consumption_log")
        print(f"   Consumption logs: {cur.fetchone()[0]}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_all_data()