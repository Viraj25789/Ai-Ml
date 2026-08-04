import pandas as pd
import os

def run_analysis():
    if not os.path.exists('data/clean_books.csv'):
        print("Error: data/clean_books.csv not found. Run cleaner.py first.")
        return

    # 1. Load the clean dataset
    print("Loading clean data...")
    df = pd.read_csv('data/clean_books.csv')

    # 2. High-Level Summary Statistics
    print("\n--- High Level Summary ---")
    print(df.describe().round(2))

    # 3. Business Question: Does a higher price mean a higher rating?
    print("\n--- Average Price by Star Rating ---")
    price_by_rating = df.groupby('Rating')['Price'].mean().round(2)
    print(price_by_rating)

    # 4. Business Question: Is there a statistical correlation?
    correlation = df['Price'].corr(df['Rating'])
    print(f"\nCorrelation between Price and Rating: {correlation:.4f}")
    if abs(correlation) < 0.1:
        print("Insight: Price has almost no impact on the book's rating.")

    # 5. Inventory Insights
    total_books = len(df)
    in_stock_books = df['In_Stock'].sum()
    stock_percentage = (in_stock_books / total_books) * 100
    print(f"\n--- Inventory Status ---")
    print(f"Overall in-stock rate: {stock_percentage:.1f}%")

if __name__ == "__main__":
    run_analysis()