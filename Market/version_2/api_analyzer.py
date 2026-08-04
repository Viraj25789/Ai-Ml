import logging
import pandas as pd
from database import CryptoDatabase

# Ensure logging matches the pipeline
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarketAnalyzer:
    """Analyzes live and historical financial data from the SQL database."""

    def __init__(self):
        self.db = CryptoDatabase()

    def run_live_report(self):
        """Generates a market report based on the most recent API pull."""
        
        # SQL query to get the most recent data batch
        query = """
        SELECT asset_name, current_price, price_change_24h 
        FROM market_data 
        WHERE extracted_at = (SELECT MAX(extracted_at) FROM market_data)
        ORDER BY price_change_24h DESC;
        """
        
        df = self.db.execute_query(query)
        
        if df is None or df.empty:
            logging.error("No data found in the database. Run the pipeline first.")
            return

        print("\n==========================================")
        print("      LIVE MARKET SQL REPORT              ")
        print("==========================================")
        
        top_gainer = df.iloc[0]
        top_loser = df.iloc[-1]
        avg_change = df['price_change_24h'].mean()
        
        print(f"🚀 Top Gainer: {top_gainer['asset_name']} (+{top_gainer['price_change_24h']:.2f}%)")
        print(f"📉 Top Loser:  {top_loser['asset_name']} ({top_loser['price_change_24h']:.2f}%)")
        
        sentiment = "Bullish" if avg_change > 0 else "Bearish"
        print(f"📊 Market Sentiment: {sentiment} ({avg_change:.2f}% avg change)")
        print("==========================================\n")

if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    analyzer.run_live_report()