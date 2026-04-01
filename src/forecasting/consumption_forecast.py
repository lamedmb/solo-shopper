"""
Consumption Forecasting
Predicts weekly consumption for each product using exponential smoothing
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db_connection import execute_query


def get_consumption_history(product_id, weeks=8):
    """
    Get historical consumption data for a product
    
    Args:
        product_id: Product ID
        weeks: Number of weeks of history to fetch
    
    Returns:
        DataFrame with consumption history
    """
    query = """
    SELECT 
        cl.week_ending,
        cl.proportion_consumed,
        cl.proportion_wasted,
        p.price_paid
    FROM consumption_log cl
    JOIN purchases p ON cl.purchase_id = p.purchase_id
    WHERE p.product_id = %s
        AND cl.week_ending >= CURRENT_DATE - INTERVAL '%s weeks'
    ORDER BY cl.week_ending
    """
    
    data = execute_query(query, (product_id, weeks))
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df['week_ending'] = pd.to_datetime(df['week_ending'])
    df['proportion_consumed'] = df['proportion_consumed'].astype(float)
    df['proportion_wasted'] = df['proportion_wasted'].astype(float)
    
    return df


def forecast_next_week_consumption(product_id, product_name):
    """
    Forecast next week's consumption for a product
    
    Returns:
        dict with forecast and confidence
    """
    
    # Get historical data
    history = get_consumption_history(product_id)
    
    if history is None or len(history) < 3:
        return {
            'product_id': product_id,
            'product_name': product_name,
            'forecast': None,
            'confidence': 'low',
            'message': 'Insufficient data (need at least 3 weeks)'
        }
    
    # Simple exponential smoothing
    consumption_rate = history['proportion_consumed'].values
    
    # Calculate simple moving average with more weight on recent weeks
    if len(consumption_rate) >= 4:
        # Weighted average: 40% last week, 30% week before, 20%, 10%
        weights = np.array([0.1, 0.2, 0.3, 0.4])
        forecast = np.average(consumption_rate[-4:], weights=weights)
        confidence = 'high'
    elif len(consumption_rate) == 3:
        # Simple average of last 3 weeks
        forecast = consumption_rate.mean()
        confidence = 'medium'
    else:
        # Just use the average
        forecast = consumption_rate.mean()
        confidence = 'low'
    
    # Calculate waste forecast
    waste_rate = history['proportion_wasted'].values
    if len(waste_rate) >= 4:
        waste_forecast = np.average(waste_rate[-4:], weights=weights)
    else:
        waste_forecast = waste_rate.mean()
    
    return {
        'product_id': product_id,
        'product_name': product_name,
        'forecast_consumption': round(forecast, 2),
        'forecast_waste': round(waste_forecast, 2),
        'confidence': confidence,
        'weeks_of_data': len(history),
        'avg_consumption_rate': round(consumption_rate.mean(), 2),
        'consumption_trend': 'increasing' if consumption_rate[-1] > consumption_rate.mean() else 'decreasing'
    }


def forecast_all_products():
    """
    Generate forecasts for all products with sufficient history
    
    Returns:
        List of forecast dictionaries
    """
    
    # Get all products that have been purchased
    products_query = """
    SELECT DISTINCT p.product_id, prod.name
    FROM purchases p
    JOIN products prod ON p.product_id = prod.product_id
    ORDER BY prod.name
    """
    
    products = execute_query(products_query)
    
    forecasts = []
    
    for product in products:
        forecast = forecast_next_week_consumption(
            product['product_id'],
            product['name']
        )
        forecasts.append(forecast)
    
    return forecasts


if __name__ == "__main__":
    print("🔮 CONSUMPTION FORECASTING")
    print("=" * 60)
    
    forecasts = forecast_all_products()
    
    print(f"\nGenerated forecasts for {len(forecasts)} products\n")
    
    for f in forecasts:
        # Check if forecast has consumption data (handle both key variations)
        if f.get('forecast_consumption') is not None:
            print(f"📦 {f['product_name']}")
            print(f"   Forecast: {f['forecast_consumption']*100:.0f}% consumption, {f['forecast_waste']*100:.0f}% waste")
            print(f"   Confidence: {f['confidence']} ({f['weeks_of_data']} weeks of data)")
            print(f"   Trend: {f['consumption_trend']}")
            print()
        elif f.get('forecast') is not None:
            # Handle old key name if it exists
            print(f"📦 {f['product_name']}")
            print(f"   {f.get('message', 'No forecast available')}")
            print()