
# Book Price Intelligence Pipeline

An end-to-end Python data analytics project that collects book catalog data, cleans and validates records, stores them in SQLite, and generates business insights using Pandas and SQL.

## Project Overview

This project demonstrates a practical data pipeline using a real-world style workflow:

1. Extract book information from Books to Scrape.
2. Clean prices, ratings, titles, and stock information.
3. Validate records and remove invalid data.
4. Store the latest catalog in SQLite.
5. Analyze prices, ratings, and stock availability.
6. Generate an executive summary report.

## Architecture

```text
Books to Scrape Website
         |
         v
    scraper.py
         |
         v
  data/raw_books.csv
         |
         v
    cleaner.py
         |
         +------> data/clean_books.csv
         |
         v
    database.py
         |
         v
   SQLite Database
         |
         v
    analysis.py
         |
         v
  Business Insights
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline development |
| Requests | HTTP requests |
| BeautifulSoup | HTML parsing |
| Pandas | Data cleaning and analysis |
| SQLite | Data storage |
| SQL | Data retrieval |
| Pytest | Automated testing |

## Project Structure

```text
version_4/
│
├── data/
│   ├── raw_books.csv
│   ├── clean_books.csv
│   └── ecommerce_catalog.db
│
├── scraper.py
├── cleaner.py
├── database.py
├── analysis.py
├── test_pipeline.py
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Viraj25789/Ai-Ml.git
```

### 2. Navigate to the project

```bash
cd Ai-Ml
cd "Data-Analytics/Book Price Intelligence/version_4"
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Pipeline

Execute these commands in order from the `version_4` directory.

**Step 1 — Extract data**

```bash
python scraper.py
```

Scrapes five catalog pages and saves the results to `data/raw_books.csv`.

**Step 2 — Clean and store data**

```bash
python cleaner.py
```

Validates records, exports the cleaned CSV, and refreshes the SQLite database.

**Step 3 — Generate analysis**

```bash
python analysis.py
```

Generates a report containing catalog statistics, inventory availability, price extremes, and price-rating correlation.

## Run Tests

```bash
pytest test_pipeline.py -v
```

The test suite checks:

- Price and rating conversion.
- Stock status conversion.
- Invalid record removal.
- Missing column validation.
- Empty dataset handling.
- Database insertion.
- Duplicate prevention.
- Data preservation after invalid input.

## Database Design

The SQLite database contains a `books` table.

| Column | Description |
|---|---|
| id | Unique book record ID |
| title | Book title |
| price_gbp | Book price |
| rating | Rating from 1 to 5 |
| in_stock | Availability status |
| extracted_at | Database insertion timestamp |

Database constraints protect price, rating, and stock values.

## Key Business Questions

This project helps answer:

1. What is the average and median book price?
2. Which books are the cheapest and most expensive?
3. How many books are currently available?
4. What is the average price for each rating?
5. Is there a linear relationship between price and rating?

## Data Source

[Books to Scrape](https://books.toscrape.com/)

A demonstration e-commerce website intended for practicing web scraping.

## Future Improvements

- Add scheduled data collection.
- Track historical price changes.
- Create interactive dashboards.
- Add more detailed SQL analysis.
- Monitor catalog changes over time.

## Author

**Viraj Parmar**

GitHub: [Viraj25789](https://github.com/Viraj25789)
