"""
Manual Price Entry Tool
Quick CLI for logging prices you see while shopping online
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db_connection import execute_query, get_connection


def get_products():
    """Get all products"""
    query = "SELECT product_id, name FROM products ORDER BY name"
    return execute_query(query)


def log_price_manually():
    """Interactive price logging"""
    print("=" * 60)
    print("🛒 MANUAL PRICE LOGGER")
    print("=" * 60)
    
    products = get_products()
    
    print(f"\n📦 You have {len(products)} products\n")
    
    # Show products with numbers
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name']}")
    
    print("\n" + "=" * 60)
    
    # Get user input
    product_num = int(input("\nSelect product number (or 0 to quit): "))
    
    if product_num == 0:
        return
    
    product = products[product_num - 1]
    
    print(f"\n📦 Selected: {product['name']}")
    
    store = input("Store (Tesco/Sainsburys): ").strip()
    regular_price = float(input("Regular price (£): "))
    
    has_promo = input("Clubcard/Nectar price? (y/n): ").lower()
    promo_price = None
    promo_type = None
    
    if has_promo == 'y':
        promo_price = float(input("Promotional price (£): "))
        promo_type = "Clubcard Price" if store == "Tesco" else "Nectar Price"
    
    # Save to database
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO price_history 
            (date, product_id, store, regular_price, promotional_price, promotion_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, product_id, store) 
            DO UPDATE SET 
                regular_price = EXCLUDED.regular_price,
                promotional_price = EXCLUDED.promotional_price,
                promotion_type = EXCLUDED.promotion_type
        """, (date.today(), product['product_id'], store, regular_price, promo_price, promo_type))
        
        conn.commit()
        print(f"\n✅ Saved: {product['name']} - {store} - £{regular_price}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()
    
    # Ask if they want to log another
    another = input("\nLog another price? (y/n): ").lower()
    if another == 'y':
        log_price_manually()


if __name__ == "__main__":
    log_price_manually()