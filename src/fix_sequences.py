"""Fix PostgreSQL sequences after loading synthetic data"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from database.db_connection import get_connection

def fix_sequences():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Fix products sequence
        cur.execute("""
            SELECT setval('products_product_id_seq', 
                         (SELECT MAX(product_id) FROM products));
        """)
        
        # Fix purchases sequence
        cur.execute("""
            SELECT setval('purchases_purchase_id_seq', 
                         (SELECT MAX(purchase_id) FROM purchases));
        """)
        
        conn.commit()
        print("✅ Fixed sequences!")
        print("   Products sequence reset")
        print("   Purchases sequence reset")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_sequences()