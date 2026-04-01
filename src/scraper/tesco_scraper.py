"""
Tesco Price Scraper
Scrapes product prices from Tesco website
"""

from playwright.sync_api import sync_playwright
import time
import re

def scrape_tesco_product(product_name: str, search_term: str = None):
    """
    Scrape price for a single product from Tesco
    
    Args:
        product_name: Full product name (e.g., "Spinach 200g")
        search_term: Optional simplified search term (e.g., "spinach")
    
    Returns:
        dict with price info or None if not found
    """
    
    if not search_term:
        # Extract search term from product name (first word usually)
        search_term = product_name.split()[0].lower()
    
    print(f"🔍 Searching Tesco for: {product_name} (search: {search_term})")
    
    try:
        with sync_playwright() as p:
            # Launch browser (headless mode)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to Tesco groceries
            tesco_url = f"https://www.tesco.com/groceries/en-GB/search?query={search_term}"
            page.goto(tesco_url, wait_until='networkidle', timeout=30000)
            
            # Wait for products to load
            time.sleep(2)
            
            # Find first product card
            try:
                # Tesco's product card selectors (these may change!)
                product_card = page.locator('li[class*="product-list"] a[data-auto*="product-tile"]').first
                
                # Get product title
                title_elem = product_card.locator('[data-auto="product-tile--title"]')
                title = title_elem.inner_text() if title_elem.count() > 0 else "Unknown"
                
                # Get regular price
                price_elem = product_card.locator('[data-auto="product-price-wrapper"] [class*="price"]')
                price_text = price_elem.inner_text() if price_elem.count() > 0 else "0"
                
                # Clean price (remove £ and convert to float)
                regular_price = float(re.sub(r'[^\d.]', '', price_text))
                
                # Check for Clubcard price
                clubcard_elem = product_card.locator('[data-auto*="clubcard"]')
                clubcard_price = None
                
                if clubcard_elem.count() > 0:
                    clubcard_text = clubcard_elem.inner_text()
                    clubcard_price = float(re.sub(r'[^\d.]', '', clubcard_text))
                
                browser.close()
                
                return {
                    'product_name': title,
                    'regular_price': regular_price,
                    'clubcard_price': clubcard_price,
                    'store': 'Tesco',
                    'found': True
                }
                
            except Exception as e:
                print(f"   ❌ Error parsing Tesco product: {e}")
                browser.close()
                return None
                
    except Exception as e:
        print(f"   ❌ Error scraping Tesco: {e}")
        return None


def scrape_all_tesco_products(products_list):
    """
    Scrape prices for multiple products from Tesco
    
    Args:
        products_list: List of dicts with 'product_id', 'name'
    
    Returns:
        List of price results
    """
    results = []
    
    for product in products_list:
        result = scrape_tesco_product(product['name'])
        
        if result:
            result['product_id'] = product['product_id']
            results.append(result)
        
        # Be nice to Tesco's servers - wait between requests
        time.sleep(3)
    
    return results


# Test function
if __name__ == "__main__":
    # Test with a single product
    test_result = scrape_tesco_product("Spinach 200g", "spinach")
    print("\n📊 Test Result:")
    print(test_result)