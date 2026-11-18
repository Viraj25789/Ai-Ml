# E-Commerce Price Intelligence Pipeline

An automated data pipeline that extracts, cleans, and analyzes product data from an e-commerce storefront. This project demonstrates end-to-end data extraction and exploratory data analysis (EDA) using Python.

## 🚀 Project Overview
The pipeline consists of three main components:
1. **Extraction:** A web scraper built with `BeautifulSoup` and `requests` that navigates pagination and extracts raw HTML product data.
2. **Cleaning:** A transformation script using `pandas` to clean currency symbols, normalize text strings into integers, and handle missing data.
3. **Analysis:** A statistical breakdown of pricing trends and correlations.

## 🛠️ Tech Stack
* **Python 3.x**
* **BeautifulSoup4** (HTML Parsing)
* **Requests** (HTTP Navigation)
* **Pandas** (Data Manipulation & Analytics)

## 📊 Key Business Insights
Based on the initial dataset extracted:
* **Price vs. Quality:** There is no statistically significant correlation between a book's price and its star rating.
* **Pricing Distribution:** The average price across the catalog sits at approximately £35, with a standard deviation indicating a wide spread of pricing tiers. 

## ⚙️ How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/price-intelligence-pipeline.git](https://github.com/yourusername/price-intelligence-pipeline.git)
   cd price-intelligence-pipeline