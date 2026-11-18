import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import logging
from typing import List, Dict, Optional

# --- 1. SETUP ENTERPRISE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

class ECommerceScraper:
    """
    An industry-standard web scraper for extracting product catalog data.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Add headers to mimic a real browser (Standard industry practice)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        os.makedirs('data', exist_ok=True)

    def fetch_page(self, page_num: int) -> Optional[BeautifulSoup]:
        """Fetches the HTML content of a specific page with error handling."""
        url = self.base_url.format(page_num)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status() # Raises an error for 404 or 500 status codes
            return BeautifulSoup(response.text, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error on page {page_num}: {e}")
            return None

    def extract_books(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Parses the HTML soup and extracts book details."""
        page_data = []
        books = soup.find_all('article', class_='product_pod')
        
        for book in books:
            try:
                title = book.h3.a['title']
                price = book.find('p', class_='price_color').text
                stock = book.find('p', class_='instock availability').text.strip()
                rating = book.find('p', class_='star-rating')['class'][1]
                
                page_data.append({
                    'Title': title,
                    'Price': price,
                    'Stock_Status': stock,
                    'Rating': rating
                })
            except AttributeError as e:
                logging.warning(f"Failed to parse a book element: {e}")
                continue # Skip broken items but keep the scraper running
                
        return page_data

    def run(self, num_pages: int = 5) -> None:
        """Executes the extraction pipeline."""
        logging.info(f"Initializing scraper pipeline for {num_pages} pages.")
        all_books = []
        
        for page in range(1, num_pages + 1):
            soup = self.fetch_page(page)
            if not soup:
                logging.warning(f"Skipping page {page} due to fetch failure.")
                continue
                
            books = self.extract_books(soup)
            all_books.extend(books)
            logging.info(f"Successfully extracted {len(books)} items from page {page}")
            
            time.sleep(1) # Rate limiting compliance
            
        # Export
        if all_books:
            df = pd.DataFrame(all_books)
            df.to_csv('data/raw_books.csv', index=False)
            logging.info(f"Pipeline complete. {len(all_books)} records saved to data/raw_books.csv")
        else:
            logging.error("Pipeline failed: No data extracted.")

if __name__ == "__main__":
    TARGET_URL = "https://books.toscrape.com/catalogue/page-{}.html"
    scraper = ECommerceScraper(base_url=TARGET_URL)
    scraper.run(num_pages=5)