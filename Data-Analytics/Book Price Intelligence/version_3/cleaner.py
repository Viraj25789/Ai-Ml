import pandas as pd
import os

def clean_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run scraper.py first.")
        return

    print("Loading raw data...")
    df = pd.read_csv(input_file)
    
    # 1. Clean Price: Remove the '£' symbol and convert to a float
    df['Price'] = df['Price'].str.replace('Â£', '').astype(float)
    
    # 2. Clean Rating: Map string ratings to actual integers
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    df['Rating'] = df['Rating'].map(rating_map)
    
    # 3. Clean Stock: Convert the text into a simple True/False boolean
    df['In_Stock'] = df['Stock_Status'].str.contains('In stock', case=False)
    
    # Drop the old messy stock column
    df.drop(columns=['Stock_Status'], inplace=True)
    
    # Export clean data
    df.to_csv(output_file, index=False)
    print(f"Clean data saved to {output_file}")
    
    # Preview the clean dataset
    print("\nData Preview:")
    print(df.head())

if __name__ == "__main__":
    clean_data('data/raw_books.csv', 'data/clean_books.csv')