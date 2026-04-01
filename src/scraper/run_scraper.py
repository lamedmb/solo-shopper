"""
Main Scraper Runner
Orchestrates scraping from both stores and saves to database
"""

import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_connection import execute_query, get_connection
from scraper.tesco_scraper import scrape_all_tesco_products
from scraper.sainsburys_scraper import scrape_all_sainsburys_products


def get_products_to_scrape():
    """Get list of products from database"""
    query = """
    SELECT product_id, name
    FROM products
    ORDER BY name
    """
    return execute_query(query)


def save_price_to_db(price_data, scrape_date):
    """Save scraped price to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        insert_query = """
        INSERT INTO price_history 
        (date, product_id, store, regular_price, promotional_price, promotion_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date, product_id, store) 
        DO UPDATE SET 
            regular_price = EXCLUDED.regular_price,
            promotional_price = EXCLUDED.promotional_price,
            promotion_type = EXCLUDED.promotion_type
        """
        
        promotion_type = "Clubcard Price" if price_data.get('clubcard_price') else None
        
        cur.execute(insert_query, (
            scrape_date,
            price_data['product_id'],
            price_data['store'],
            price_data['regular_price'],
            price_data.get('clubcard_price') or price_data.get('promotional_price'),
            promotion_type
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return False


def run_full_scrape():
    """Run complete scraping process"""
    print("=" * 60)
    print("🛒 SOLO SHOPPER - WEEKLY PRICE SCRAPER")
    print("=" * 60)
    
    scrape_date = date.today()
    print(f"📅 Scraping date: {scrape_date}\n")
    
    # Get products to scrape
    products = get_products_to_scrape()
    print(f"📦 Found {len(products)} products to scrape\n")
    
    # Scrape Tesco
    print("🏪 Scraping Tesco...")
    print("-" * 60)
    tesco_results = scrape_all_tesco_products(products[:5])  # Start with first 5 for testing
    print(f"✅ Tesco: Found {len(tesco_results)} prices\n")
    
    # Scrape Sainsbury's
    print("🏪 Scraping Sainsbury's...")
    print("-" * 60)
    sainsburys_results = scrape_all_sainsburys_products(products[:5])  # Start with first 5
    print(f"✅ Sainsbury's: Found {len(sainsburys_results)} prices\n")
    
    # Save to database
    print("💾 Saving to database...")
    print("-" * 60)
    
    saved_count = 0
    all_results = tesco_results + sainsburys_results
    
    for result in all_results:
        if save_price_to_db(result, scrape_date):
            saved_count += 1
            print(f"   ✅ Saved: {result['product_name']} - {result['store']} - £{result['regular_price']}")
    
    print("\n" + "=" * 60)
    print(f"🎉 SCRAPE COMPLETE!")
    print(f"   Total prices saved: {saved_count}/{len(all_results)}")
    print("=" * 60)


if __name__ == "__main__":
    run_full_scrape()