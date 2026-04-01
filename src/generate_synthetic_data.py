"""
Generate synthetic grocery data for testing the Solo Shopper system
Run this once to create 8 weeks of realistic data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

# Output directory
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("🛒 Generating synthetic Solo Shopper data...\n")

# 1. PRODUCTS TABLE
print("📦 Creating products...")
products = pd.DataFrame({
    'product_id': range(1, 31),
    'name': [
        'Spinach 200g', 'Spinach 400g', 'Cherry Tomatoes 250g', 
        'Milk 1L', 'Milk 2L', 'Chicken Breast 300g', 'Chicken Breast 600g',
        'Pasta 500g', 'Rice 1kg', 'Bread', 'Eggs 6pk', 'Eggs 12pk',
        'Yogurt 4pk', 'Cheese 200g', 'Bananas 5pk', 'Apples 6pk',
        'Onions 1kg', 'Garlic Bulb', 'Tinned Tomatoes', 'Olive Oil 500ml',
        'Coffee 200g', 'Tea 80 bags', 'Butter 250g', 'Bacon 200g',
        'Salad Bag 100g', 'Hummus 200g', 'Carrots 500g', 'Broccoli',
        'Potatoes 2kg', 'Cheddar 400g'
    ],
    'category': [
        'Fresh Produce', 'Fresh Produce', 'Fresh Produce',
        'Dairy', 'Dairy', 'Meat', 'Meat',
        'Cupboard', 'Cupboard', 'Bakery', 'Dairy', 'Dairy',
        'Dairy', 'Dairy', 'Fresh Produce', 'Fresh Produce',
        'Fresh Produce', 'Fresh Produce', 'Cupboard', 'Cupboard',
        'Cupboard', 'Cupboard', 'Dairy', 'Meat',
        'Fresh Produce', 'Chilled', 'Fresh Produce', 'Fresh Produce',
        'Fresh Produce', 'Dairy'
    ],
    'typical_shelf_life_days': [
        7, 7, 10, 7, 7, 3, 3, 365, 365, 5, 21, 21,
        14, 30, 7, 10, 30, 14, 730, 365,
        180, 365, 30, 7, 5, 7, 14, 7, 60, 60
    ],
    'base_price_gbp': [
        1.20, 2.00, 1.80, 1.15, 1.95, 3.50, 6.00,
        0.95, 1.80, 1.10, 2.20, 3.80, 2.50, 2.00,
        1.00, 2.50, 0.90, 0.35, 0.55, 4.50, 5.50,
        2.50, 1.75, 2.80, 1.30, 1.60, 0.70, 1.20,
        2.00, 3.50
    ]
})

# 2. PRICE HISTORY
print("💰 Creating price history (8 weeks, Tesco vs Sainsbury's)...")
dates = pd.date_range(end=datetime.now(), periods=8, freq='W-SUN')
price_data = []

for product_id in products['product_id']:
    base_price = products.loc[products['product_id'] == product_id, 'base_price_gbp'].values[0]
    
    for week_idx, date in enumerate(dates):
        # Add some weekly variance
        weekly_variance = 1 + np.random.uniform(-0.10, 0.10)
        
        # Tesco price
        tesco_regular = base_price * weekly_variance * np.random.uniform(0.98, 1.05)
        has_clubcard = np.random.random() < 0.35  # 35% of items have Clubcard price
        
        if has_clubcard:
            # 70% real discount, 30% anchor pricing
            if np.random.random() < 0.7:
                clubcard_price = tesco_regular * np.random.uniform(0.70, 0.88)  # Real discount
            else:
                clubcard_price = tesco_regular * np.random.uniform(0.95, 1.02)  # Fake discount!
        else:
            clubcard_price = None
            
        # Sainsbury's price (usually within 5% of Tesco)
        sainsburys_price = base_price * weekly_variance * np.random.uniform(0.96, 1.06)
        
        price_data.append({
            'date': date.date(),
            'product_id': product_id,
            'store': 'Tesco',
            'regular_price': round(tesco_regular, 2),
            'promotional_price': round(clubcard_price, 2) if clubcard_price else None,
            'promotion_type': 'Clubcard Price' if clubcard_price else None
        })
        
        price_data.append({
            'date': date.date(),
            'product_id': product_id,
            'store': 'Sainsburys',
            'regular_price': round(sainsburys_price, 2),
            'promotional_price': None,
            'promotion_type': None
        })

price_history = pd.DataFrame(price_data)

# 3. PURCHASES
print("🧾 Creating purchase history (8 weekly shops)...")
purchases = []
purchase_id = 1

for week in range(8):
    shop_date = dates[week].date()
    
    # Weekly staples (buy every week)
    staples = [1, 4, 10, 11, 13, 20, 22]  # spinach, milk, bread, eggs, yogurt, coffee, tea
    
    # Rotating purchases (every 2-3 weeks)
    rotating = np.random.choice([6, 8, 9, 15, 16, 19, 23, 27, 29], 
                                size=np.random.randint(3, 5), replace=False)
    
    # Variable purchases (sometimes)
    variable = np.random.choice([3, 14, 24, 25, 26, 28], 
                               size=np.random.randint(1, 3), replace=False)
    
    items_bought = list(staples) + list(rotating) + list(variable)
    
    for product_id in items_bought:
        # Get prices for this product this week
        product_prices = price_history[
            (price_history['product_id'] == product_id) & 
            (price_history['date'] == shop_date)
        ].copy()
        
        # Calculate effective price (promotional if available, otherwise regular)
        product_prices['effective_price'] = product_prices.apply(
            lambda x: x['promotional_price'] if pd.notna(x['promotional_price']) else x['regular_price'], 
            axis=1
        )
        
        # Choose cheapest option 70% of time
        if np.random.random() < 0.7:
            # Find row with minimum effective price
            min_idx = product_prices['effective_price'].idxmin()
            cheapest = product_prices.loc[min_idx]
            store = cheapest['store']
            price_paid = cheapest['effective_price']
            promo_used = pd.notna(cheapest['promotional_price'])
        else:
            # Just go to Tesco (convenience)
            tesco = product_prices[product_prices['store'] == 'Tesco'].iloc[0]
            store = 'Tesco'
            if pd.notna(tesco['promotional_price']) and np.random.random() < 0.8:
                price_paid = tesco['promotional_price']
                promo_used = True
            else:
                price_paid = tesco['regular_price']
                promo_used = False
        
        purchases.append({
            'purchase_id': purchase_id,
            'date': shop_date,
            'product_id': product_id,
            'store': store,
            'price_paid': round(float(price_paid), 2),
            'promotional_price_used': promo_used
        })
        purchase_id += 1

purchases_df = pd.DataFrame(purchases)

# 4. CONSUMPTION LOG
print("📊 Creating consumption & waste log...")
consumption = []

for week in range(8):
    week_date = dates[week].date()
    week_purchases = purchases_df[purchases_df['date'] == week_date]
    
    for _, purchase in week_purchases.iterrows():
        product = products[products['product_id'] == purchase['product_id']].iloc[0]
        
        # Waste rate by category (fresh produce wastes most)
        if product['category'] == 'Fresh Produce':
            waste_rate = np.random.uniform(0.20, 0.50)
        elif product['category'] == 'Bakery':
            waste_rate = np.random.uniform(0.10, 0.30)
        elif product['category'] in ['Dairy', 'Chilled']:
            waste_rate = np.random.uniform(0.05, 0.20)
        elif product['category'] == 'Meat':
            waste_rate = np.random.uniform(0.0, 0.15)
        else:  # Cupboard items
            waste_rate = np.random.uniform(0.0, 0.05)
        
        quantity_consumed = 1 - waste_rate
        
        # Waste reasons
        if waste_rate > 0.10:
            reasons = ['Expired before use', 'Over-bought', 'Didn\'t cook as planned', 'Went bad']
            waste_reason = np.random.choice(reasons)
        else:
            waste_reason = None
        
        consumption.append({
            'purchase_id': purchase['purchase_id'],
            'week_ending': week_date,
            'proportion_consumed': round(quantity_consumed, 2),
            'proportion_wasted': round(waste_rate, 2),
            'waste_reason': waste_reason,
            'waste_cost_gbp': round(purchase['price_paid'] * waste_rate, 2)
        })

consumption_log = pd.DataFrame(consumption)

# 5. SAVE TO CSV
print("\n💾 Saving files...")
products.to_csv(DATA_DIR / 'products.csv', index=False)
price_history.to_csv(DATA_DIR / 'price_history.csv', index=False)
purchases_df.to_csv(DATA_DIR / 'purchases.csv', index=False)
consumption_log.to_csv(DATA_DIR / 'consumption_log.csv', index=False)

# 6. SUMMARY STATS
print("\n✅ Synthetic data generated successfully!\n")
print("=" * 50)
print(f"📦 Products: {len(products)}")
print(f"💰 Price records: {len(price_history)} ({len(price_history)//len(products)} weeks)")
print(f"🧾 Purchases: {len(purchases_df)}")
print(f"📊 Consumption logs: {len(consumption_log)}")
print(f"📅 Date range: {dates[0].date()} to {dates[-1].date()}")
print("=" * 50)

# Analysis preview
total_spent = purchases_df['price_paid'].sum()
total_wasted = consumption_log['waste_cost_gbp'].sum()
waste_pct = (total_wasted / total_spent) * 100

print(f"\n💸 Total spent: £{total_spent:.2f}")
print(f"🗑️  Total wasted: £{total_wasted:.2f} ({waste_pct:.1f}%)")
print(f"\nFiles saved to: {DATA_DIR.absolute()}")