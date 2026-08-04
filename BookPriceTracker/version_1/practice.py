import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time


os.makedirs("output", exist_ok=True)

url = "https://books.toscrape.com"

response = requests.get(url)

if response.status_code == 200:

    soup = BeautifulSoup(response.text, "html.parser")

# #   print(response.status_code)
# #   print(response.headers)
# #   print(type(response.text))
# #   print(type(soup))

# #   print(soup.title) # full tag

#     #  .text .get_text()  BOTH GIVES TEXT OF TITLE
# #   print(soup.title.text)

# #   print(soup.title.name)
# #   print(soup.title.parent.name)

# #   book = soup.find("a")
# #   print(book)

# #   print(book["href"]) #   returns attribute value
# #   or direct in book
# #   book = soup.find("a")["href"]

#     book = soup.find("article", class_="product_pod") # class is reserved keywd so use class_
#     # print(book)
#     # print(type(book))

#     title = book.find("h3").find("a")["title"]

#     link = book.find("h3").find("a")["href"]

#     price = book.find("p", class_="price_color").text

#     availability = book.find("p", class_="instock availability").text.strip()

#     rating = book.find("p", class_="star-rating")["class"][1]

#     print("=" * 40)
#     print("Title       :", title)
#     print("Price       :", price)
#     print("Availability:", availability)
#     print("Rating      :", rating)
#     print("Link        :", link)
#     print("=" * 40)

    books = soup.find_all("article", class_="product_pod")
    all_books = []

    for book in books:
        book_link = book.find("h3").find("a")
        title = book_link["title"]
        link = book_link["href"]
        price = book.find("p", class_="price_color").text
        availability = book.find("p", class_="instock availability").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]

        # print("=" * 40)
        # print("Title       :", title)
        # print("Price       :", price)
        # print("Availability:", availability)
        # print("Rating      :", rating)
        # print("Link        :", link)
        # print("=" * 40)

        data = {
                    "title": title,
                    "link": link,
                    "price": price,
                    "availability": availability,
                    "rating": rating
                }
        all_books.append(data)

else:
    print("Failed to load page:", response.status_code)




''' ____________________________________________________________________'''

df = pd.DataFrame(all_books)

# print(df)
# print(df.head())
# print(df.tail())
# print(df.shape)
# print(df.columns)
# print(df.dtypes)
# print(df.info())
# print(df.describe(include="all"))
# print(df["title"])
# print(df[["title", "price"]])
# print(df.iloc[0])
# print(df.iloc[0]["title"])

df["price"] = df["price"].str.replace("Â£", "", regex=False)
df["price"] = df["price"].astype(float)

# print(df["price"].mean())
# print(df["price"].max())
# print(df["price"].min())
# print(df["price"].sum())
# print(df["price"].count())

# # Filtering
# expensive_books = df[df["price"] > 50]
# cheap_books = df[df["price"] < 20]
# five_star = df[df["rating"] == "Five"]
# result = df[
#     (df["rating"] == "Five") &
#     (df["price"] > 40)
# ]

# # Sorting
# print(df.sort_values("price", ascending=False))
# print(df.sort_values("price"))
# top5 = df.sort_values("price",ascending=False). head(5)

# Export
df.to_csv(
    "output/books_csv.csv",
    index=False
)

df.to_json(
    "output/books.json",
    orient="records",
    index=False
)