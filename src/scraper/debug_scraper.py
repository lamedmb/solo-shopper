"""
Debug script to inspect actual HTML from Tesco and Sainsbury's
"""

from playwright.sync_api import sync_playwright
import time

def debug_tesco():
    """Open Tesco in browser and save HTML"""
    print("🔍 Opening Tesco...")
    
    with sync_playwright() as p:
        # Launch in non-headless mode so you can see it
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Search for spinach
        page.goto("https://www.tesco.com/groceries/en-GB/search?query=spinach", wait_until='networkidle')
        
        # Wait for page to fully load
        time.sleep(5)
        
        # Save the HTML
        html = page.content()
        with open('tesco_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✅ Saved to tesco_debug.html")
        print("🔍 Keeping browser open for 30 seconds so you can inspect...")
        
        # Keep browser open so you can inspect
        time.sleep(30)
        
        browser.close()


def debug_sainsburys():
    """Open Sainsbury's in browser and save HTML"""
    print("🔍 Opening Sainsbury's...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://www.sainsburys.co.uk/gol-ui/SearchResults/spinach", wait_until='networkidle')
        
        time.sleep(5)
        
        html = page.content()
        with open('sainsburys_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✅ Saved to sainsburys_debug.html")
        print("🔍 Keeping browser open for 30 seconds so you can inspect...")
        
        time.sleep(30)
        
        browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("WEB SCRAPER DEBUGGER")
    print("=" * 60)
    
    choice = input("\nDebug (1) Tesco or (2) Sainsbury's? [1/2]: ")
    
    if choice == "1":
        debug_tesco()
    elif choice == "2":
        debug_sainsburys()
    else:
        print("Invalid choice")