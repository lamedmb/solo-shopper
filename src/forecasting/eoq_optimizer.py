"""
Economic Order Quantity (EOQ) Calculator
Determines optimal purchase quantity and frequency
"""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db_connection import execute_query


def calculate_eoq(product_id, product_name, weekly_consumption_rate, current_price):
    """
    Calculate optimal order quantity using EOQ model
    
    Args:
        product_id: Product ID
        product_name: Product name
        weekly_consumption_rate: Proportion consumed per week (0-1)
        current_price: Current price in GBP
    
    Returns:
        dict with EOQ recommendations
    """
    
    # Get product shelf life
    shelf_life_query = """
    SELECT typical_shelf_life_days 
    FROM products 
    WHERE product_id = %s
    """
    result = execute_query(shelf_life_query, (product_id,))
    
    if not result:
        return None
    
    shelf_life_days = result[0]['typical_shelf_life_days']
    shelf_life_weeks = shelf_life_days / 7
    
    # Calculate optimal order frequency
    # If you consume X% per week and product lasts Y weeks, you should buy every Z weeks
    
    if weekly_consumption_rate <= 0:
        return {
            'product_name': product_name,
            'recommendation': 'DO NOT BUY',
            'reason': 'Not consuming this item'
        }
    
    # Weeks until you'll consume one unit
    weeks_to_consume = 1 / weekly_consumption_rate
    
    # Optimal purchase frequency (accounting for shelf life)
    if weeks_to_consume > shelf_life_weeks:
        # You consume it slower than it expires
        recommendation = f"Buy smaller pack or skip - expires before you finish"
        purchase_frequency_weeks = None
        waste_risk = 'HIGH'
    elif weeks_to_consume < 1:
        # You consume more than 1 per week
        recommendation = f"Buy every week (you consume {1/weeks_to_consume:.1f} per week)"
        purchase_frequency_weeks = 1
        waste_risk = 'LOW'
    else:
        # Normal case
        recommendation = f"Buy every {int(np.ceil(weeks_to_consume))} weeks"
        purchase_frequency_weeks = int(np.ceil(weeks_to_consume))
        waste_risk = 'LOW' if purchase_frequency_weeks < shelf_life_weeks * 0.5 else 'MEDIUM'
    
    # Calculate cost efficiency
    cost_per_week = current_price / weeks_to_consume if weeks_to_consume > 0 else 0
    
    return {
        'product_id': product_id,
        'product_name': product_name,
        'consumption_rate_per_week': round(weekly_consumption_rate, 2),
        'weeks_to_consume_one_unit': round(weeks_to_consume, 1),
        'shelf_life_weeks': round(shelf_life_weeks, 1),
        'recommendation': recommendation,
        'purchase_frequency_weeks': purchase_frequency_weeks,
        'waste_risk': waste_risk,
        'cost_per_week': round(cost_per_week, 2),
        'current_price': current_price
    }


def generate_shopping_list_recommendations():
    """
    Generate shopping list based on EOQ and forecasts
    """
    from forecasting.consumption_forecast import forecast_all_products
    
    forecasts = forecast_all_products()
    
    recommendations = []
    
    for forecast in forecasts:
        # Skip if no forecast data
        if forecast.get('forecast_consumption') is None:
            continue
        
        # Get latest price
        price_query = """
        SELECT price_paid
        FROM purchases
        WHERE product_id = %s
        ORDER BY date DESC
        LIMIT 1
        """
        
        price_result = execute_query(price_query, (forecast['product_id'],))
        
        if not price_result:
            continue
        
        current_price = float(price_result[0]['price_paid'])
        
        # Calculate EOQ
        eoq = calculate_eoq(
            forecast['product_id'],
            forecast['product_name'],
            forecast['forecast_consumption'],
            current_price
        )
        
        if eoq:
            recommendations.append(eoq)
    
    return recommendations


if __name__ == "__main__":
    print("📊 EOQ OPTIMIZATION")
    print("=" * 60)
    
    recommendations = generate_shopping_list_recommendations()
    
    print(f"\nGenerated {len(recommendations)} recommendations\n")
    
    # Group by waste risk
    high_risk = [r for r in recommendations if r.get('waste_risk') == 'HIGH']
    medium_risk = [r for r in recommendations if r.get('waste_risk') == 'MEDIUM']
    low_risk = [r for r in recommendations if r.get('waste_risk') == 'LOW']
    
    if high_risk:
        print("🚨 HIGH WASTE RISK:")
        for r in high_risk:
            print(f"   {r['product_name']}: {r['recommendation']}")
        print()
    
    if medium_risk:
        print("⚠️  MEDIUM WASTE RISK:")
        for r in medium_risk:
            print(f"   {r['product_name']}: {r['recommendation']}")
        print()
    
    if low_risk:
        print("✅ LOW WASTE RISK:")
        for r in low_risk[:5]:  # Show first 5
            print(f"   {r['product_name']}: {r['recommendation']}")