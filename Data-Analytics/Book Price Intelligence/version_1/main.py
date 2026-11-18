import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# Create output folder if it doesn't exist
os.makedirs("output", exist_ok=True)

# Store all books here
all_books = []

session = requests.Session()

# Scrape all 50 pages
for page in range(1, 51):

    print(f"Scraping Page {page}...")

    url = f"https://books.toscrape.com/catalogue/page-{page}.html"

    response = session.get(url)

    # Check if request was successful
    if response.status_code != 200:
        print(f"Failed to fetch Page {page}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    for book in books:

        book_link = book.find("h3").find("a")

        title = book_link["title"]
        link = "https://books.toscrape.com/catalogue/" + book_link["href"]

        price = book.find("p", class_="price_color").text
        availability = book.find("p", class_="instock availability").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]

        book_data = {
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating,
            "link": link
        }

        all_books.append(book_data)

    # Small delay to be polite to the server
    time.sleep(1)

print("\nScraping Completed!")
print(f"Total Books Scraped: {len(all_books)}")

# Create DataFrame
df = pd.DataFrame(all_books)

# Clean Price
df["price"] = df["price"].str.replace("Â£", "", regex=False)
df["price"] = df["price"].astype(float)

# Save Files
df.to_csv("output/books.csv", index=False)

print("CSV Saved Successfully!")

# Show first five rows
print("\nFirst Five Books")
print(df.head())

print("\nData Information")
print(df.info())

print("\nAverage Price:", df["price"].mean())
print("Highest Price:", df["price"].max())
print("Lowest Price:", df["price"].min())