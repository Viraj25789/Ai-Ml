import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

def scrape_books(num_pages=5):
    books_data = []
    
    print(f"Starting scraper for {num_pages} pages...")
    
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    for page in range(1, num_pages + 1):
        url = BASE_URL.format(page)
        response = requests.get(url)
        
        # Stop if we hit a page that doesn't exist
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}. Stopping.")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        
        for book in books:
            # 1. Title is stored in the 'title' attribute of the anchor tag
            title = book.h3.a['title']
            
            # 2. Price is in a specific paragraph class
            price = book.find('p', class_='price_color').text
            
            # 3. Stock availability text
            stock = book.find('p', class_='instock availability').text.strip()
            
            # 4. Rating is the second class name of the star-rating paragraph
            rating = book.find('p', class_='star-rating')['class'][1] 
            
            books_data.append({
                'Title': title,
                'Price': price,
                'Stock_Status': stock,
                'Rating': rating
            })
        
        print(f"Scraped page {page}")
        time.sleep(1) # Be polite to the server
        
    # Export to CSV
    df = pd.DataFrame(books_data)
    df.to_csv('data/raw_books.csv', index=False)
    print(f"Success! {len(books_data)} books saved to data/raw_books.csv")

if __name__ == "__main__":
    scrape_books(num_pages=5)