import pandas as pd
import os

def run_market_analysis():
    # Check data file exists before running
    if not os.path.exists('data/live_market_data.csv'):
        print("Error: No data found. Run api_extractor.py first.")
        return

    # Load dataset
    df = pd.read_csv('data/live_market_data.csv')
    
    print("\n=== LIVE MARKET ANALYSIS ===")
    
    # 1. Find the top gainer in the last 24 hours
    # .idxmax() : the index row of the highest value in the column
    top_gainer = df.loc[df['price_change_percentage_24h'].idxmax()]
    print(f"\n🚀 Top 24h Gainer: {top_gainer['name']} ({top_gainer['price_change_percentage_24h']:.2f}%)")
    
    # 2. Find the biggest loser
    # .idxmin() : the index row of the lowest value in the column
    biggest_loser = df.loc[df['price_change_percentage_24h'].idxmin()]
    print(f"📉 Biggest 24h Loser: {biggest_loser['name']} ({biggest_loser['price_change_percentage_24h']:.2f}%)")
    
    # 3. Calculate Market Sentiment (Average 24h change across top 50 assets)
    avg_change = df['price_change_percentage_24h'].mean()
    sentiment = "Bullish (Upward)" if avg_change > 0 else "Bearish (Downward)"
    print(f"\n📊 Overall Top 50 Market Sentiment: {sentiment} ({avg_change:.2f}%)")

if __name__ == "__main__":
    run_market_analysis()