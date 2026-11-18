import requests
import pandas as pd
import logging
import time
import os
from database import CryptoDatabase
from typing import Optional, List, Dict

class CoinGeckoPipeline:
    """Enterprise REST API data extraction and transformation engine."""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3/coins/markets"
        self.session = requests.Session()
        self.db = CryptoDatabase()
        os.makedirs('data', exist_ok=True)

    def fetch_api_data(self) -> Optional[List[Dict]]:
        """Handles HTTP requests, error codes, and rate limits."""
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1,
            'sparkline': False
        }

        try:
            logging.info("Initiating GET request to CoinGecko API...")
            response = self.session.get(self.base_url, params=params, timeout=10)
            
            # Handle Rate Limiting Specifically
            if response.status_code == 429:
                logging.error("API Rate Limit Exceeded (HTTP 429). Try again later.")
                return None
                
            response.raise_for_status() # Catches 404s, 500s, etc.
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during API call: {e}")
            return None

    def process_and_store(self, raw_json: List[Dict]) -> None:
        """Flattens nested JSON and triggers database storage."""
        if not raw_json:
            logging.warning("No JSON data to process.")
            return

        logging.info("Flattening nested JSON payload using pandas...")
        df = pd.json_normalize(raw_json)
        
        columns_to_keep = [
            'name', 'symbol', 'current_price', 'market_cap', 
            'price_change_percentage_24h', 'roi.percentage'
        ]
        
        clean_df = df[columns_to_keep].copy()
        clean_df.fillna(0, inplace=True)
        
        # Save to CSV for backup
        clean_df.to_csv('data/latest_market_data.csv', index=False)
        logging.info("Saved local CSV backup.")
        
        # Save to SQLite for persistence
        self.db.save_dataframe(clean_df)

    def run(self):
        """Executes the full pipeline workflow."""
        json_data = self.fetch_api_data()
        if json_data:
            self.process_and_store(json_data)
        else:
            logging.error("Pipeline failed to retrieve data. Execution halted.")

if __name__ == "__main__":
    pipeline = CoinGeckoPipeline()
    pipeline.run()