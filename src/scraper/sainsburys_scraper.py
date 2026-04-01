"""
Sainsbury's Price Scraper
Scrapes product prices from Sainsbury's website
"""

from playwright.sync_api import sync_playwright
import time
import re

def scrape_sainsburys_product(product_name: str, search_term: str = None):
    """
    Scrape price for a single product from Sainsbury's
    
    Args:
        product_name: Full product name (e.g., "Spinach 200g")
        search_term: Optional simplified search term
    
    Returns:
        dict with price info or None if not found
    """
    
    if not search_term:
        search_term = product_name.split()[0].lower()
    
    print(f"🔍 Searching Sainsbury's for: {product_name} (search: {search_term})")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to Sainsbury's
            sainsburys_url = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_term}"
            page.goto(sainsburys_url, wait_until='networkidle', timeout=30000)
            
            time.sleep(2)
            
            try:
                # Sainsbury's product card selectors (these may change!)
                product_card = page.locator('[data-testid="product-tile"]').first
                
                # Get product title
                title_elem = product_card.locator('[data-testid="product-tile-title"]')
                title = title_elem.inner_text() if title_elem.count() > 0 else "Unknown"
                
                # Get price
                price_elem = product_card.locator('[data-testid="product-tile-price"]')
                price_text = price_elem.inner_text() if price_elem.count() > 0 else "£0"
                
                # Clean price
                regular_price = float(re.sub(r'[^\d.]', '', price_text))
                
                # Sainsbury's doesn't have Clubcard equivalent, but check for Nectar prices
                nectar_price = None
                
                browser.close()
                
                return {
                    'product_name': title,
                    'regular_price': regular_price,
                    'promotional_price': nectar_price,
                    'store': 'Sainsburys',
                    'found': True
                }
                
            except Exception as e:
                print(f"   ❌ Error parsing Sainsbury's product: {e}")
                browser.close()
                return None
                
    except Exception as e:
        print(f"   ❌ Error scraping Sainsbury's: {e}")
        return None


def scrape_all_sainsburys_products(products_list):
    """
    Scrape prices for multiple products from Sainsbury's
    """
    results = []
    
    for product in products_list:
        result = scrape_sainsburys_product(product['name'])
        
        if result:
            result['product_id'] = product['product_id']
            results.append(result)
        
        time.sleep(3)
    
    return results


# Test function
if __name__ == "__main__":
    test_result = scrape_sainsburys_product("Spinach 200g", "spinach")
    print("\n📊 Test Result:")
    print(test_result)