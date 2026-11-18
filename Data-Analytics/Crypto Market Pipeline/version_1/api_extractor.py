import requests
import pandas as pd
import json
import os

def fetch_market_data():
    print("Connecting to Financial API...")
    
    # data directory exists verify
    os.makedirs('data', exist_ok=True)
    
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the JSON response into a Python list of dictionaries
        raw_json_data = response.json()
        
        df = pd.json_normalize(raw_json_data)
        
        # Select only the columns we care about for analysis
        columns_to_keep = [
            'name', 'symbol', 'current_price', 'market_cap', 
            'price_change_percentage_24h', 'roi.percentage'
        ]
        
        # Filter the dataframe and handle missing data
        clean_df = df[columns_to_keep].copy()
        clean_df.fillna(0, inplace=True) # Replace missing data with 0
        
        # 4. Export to CSV
        clean_df.to_csv('data/live_market_data.csv', index=False)
        print(f"Success! Flattened data for {len(clean_df)} assets saved to data/live_market_data.csv.")
        print("\nData Preview:")
        print(clean_df.head(3))
    else:
        print(f"API Request Failed. Status Code: {response.status_code}")

if __name__ == "__main__":
    fetch_market_data()