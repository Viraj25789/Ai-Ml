# Data Analysis & Web Scraping

Welcome to my data extraction portfolio. This repository houses a collection of automated data pipelines that I engineered to extract, clean, and analyze web data. 

The projects here demonstrate a progression from writing functional extraction scripts to architecting enterprise-grade backend microservices using Object-Oriented Programming (OOP), relational databases, and professional error handling.

## 📂 Repository Structure

This repository is divided into two main domains of data extraction: HTML Parsing and REST API Consumption. Both projects contain versioned histories showing the progression from flat-file CSV scripts to production-ready SQLite pipelines.

### 1. `📁 bookpricetracker` (E-Commerce Price Intelligence)
An automated ETL (Extract, Transform, Load) pipeline that scrapes product catalog data from an e-commerce storefront, sanitizes the data, and performs exploratory data analysis to find pricing trends.
* **Extraction:** Navigates pagination and parses raw HTML using `BeautifulSoup` and `requests`.
* **Transformation:** Uses `pandas` to clean currency symbols, normalize text strings into integers, and enforce strict domain constraints.
* **Evolution:** 
  * *Version 1:* Functional baseline extracting data to flat `.csv` files.
  * *Version 2:* Enterprise upgrade featuring an OOP architecture, robust ETL cleaning engines, and a relational `SQLite` database with compound indexing.

### 2. `📁 market` (Live Crypto Market Pipeline)
A resilient data engineering microservice that extracts real-time financial payloads from the public CoinGecko REST API, flattens the nested JSON structures, and persists the data.
* **Extraction:** Connects to public REST endpoints, managing HTTP session pooling, request timeouts, and `HTTP 429 (Rate Limit)` exception handling.
* **Transformation:** Automates the flattening of deeply nested JSON payloads using Pandas `json_normalize`.
* **Evolution:**
  * *Version 1:* Focuses on JSON parsing and Pandas data structuring.
  * *Version 2:* Production-ready system with automated error logging, rate-limit handling, and SQLite persistence to track historical market trends.

## 🛠️ Core Technologies Used
* **Languages:** Python 3.x, SQL
* **Data Extraction:** `requests`, `BeautifulSoup4`, REST APIs, JSON Parsing
* **Data Processing:** `pandas` (ETL, Data Cleaning, JSON Normalization)
* **Storage:** `SQLite3` (Relational Databases, Table Constraints, Indexing)
* **Software Engineering:** Object-Oriented Programming (OOP), `logging`, Exception Handling, Data Type Enforcement

## 🚀 How to Explore Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/scraper.git](https://github.com/yourusername/scraper.git)
   cd scraper
   
2. **Set up a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

3. **Navigate to the individual projects**
   Each sub-directory (bookpricetracker/ and market/) contains its own specific instructions, source code, and analysis scripts. Navigate into the folder of your choice to run the pipelines.

4. 
