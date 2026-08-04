import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

# -----------------------------
# Configuration
# -----------------------------
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGES = 50
OUTPUT_FOLDER = "output"

# -----------------------------
# Create Output Folder
# -----------------------------
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# Create Session
# -----------------------------
session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
})

# -----------------------------
# Store Data
# -----------------------------
all_books = []

# -----------------------------
# Scraping
# -----------------------------
for page in range(1, TOTAL_PAGES + 1):

    url = BASE_URL.format(page)

    print(f"Scraping Page {page}...")

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all("article", class_="product_pod")

        for book in books:

            book_link = book.find("h3").find("a")

            title = book_link["title"]

            link = (
                "https://books.toscrape.com/catalogue/"
                + book_link["href"]
            )

            price = book.find(
                "p",
                class_="price_color"
            ).text

            availability = book.find(
                "p",
                class_="instock availability"
            ).text.strip()

            rating = book.find(
                "p",
                class_="star-rating"
            )["class"][1]

            book_data = {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "link": link
            }

            all_books.append(book_data)

        # Be polite to the server
        time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"Error on page {page}: {e}")

# -----------------------------
# DataFrame
# -----------------------------
df = pd.DataFrame(all_books)

# -----------------------------
# Data Cleaning
# -----------------------------
df["price"] = (
    df["price"]
    .str.replace("Â£", "", regex=False)
    .astype(float)
)

# -----------------------------
# Save Files
# -----------------------------
csv_file = os.path.join(OUTPUT_FOLDER, "books.csv")

df.to_csv(csv_file, index=False)

# -----------------------------
# Analysis
# -----------------------------
print("\n========== SUMMARY ==========")
print(f"Total Books : {len(df)}")
print(f"Average Price : £{df['price'].mean():.2f}")
print(f"Highest Price : £{df['price'].max():.2f}")
print(f"Lowest Price : £{df['price'].min():.2f}")

print("\nTop 5 Books")
print(df.head())

print("\nFive-Star Books")
print(df[df["rating"] == "Five"].head())

print("\nFiles Saved Successfully!")
print(csv_file)
