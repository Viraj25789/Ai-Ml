# Enterprise E-Commerce Price Intelligence Pipeline

An end-to-end, resilient data engineering pipeline that extracts product catalog data, performs data cleaning, persists records into an SQLite relational database, and generates analytical insights.

Built using Object-Oriented Programming (OOP) principles, thread-safe database connections, error handling, logging, and unit testing.

---

## 🏗️ System Architecture & Data Flow

+--------------------------+
|  E-Commerce Target Site  |
+--------------------------+
|
|  requests.Session() (HTTPS GET / Rate Limited)
v
+--------------------------+
|   ECommerceScraper (OOP) | ---> Generates: pipeline.log
+--------------------------+
|
|  Raw CSV Ingestion (data/raw_books.csv)
v
+--------------------------+
|   DataCleaner (ETL)      | ---> Data Audit & Validation
+--------------------------+
|
|  Clean Pandas DataFrame Transformed
v
+--------------------------------------------------+
| DatabaseManager (SQLite Relational Persistence)  |
+--------------------------------------------------+
|                                          |
v                                          v
File Export: data/clean_books.csv       Table: books (Indexed Schema)
|
v
+------------------------------+
| CatalogAnalyzer (SQL Query)  |
+------------------------------+
|
v
Executive Insights Report


---

## 🛠️ Key Technical Features

1. **Robust HTTP Extraction Layer:**
   * Utilizes `requests.Session()` for connection pooling.
   * Defensive Exception handling for HTTP timeouts and status codes (`raise_for_status()`).
   * Configured request headers and server-compliant rate-limiting (`time.sleep`).

2. **Data Transformation & Integrity Engine:**
   * Regex parsing for currency strings.
   * Vectorized Pandas mappings for rating strings (`One` -> `1`).
   * Outlier and missing record filtering with automated data logging.

3. **Relational Persistence Layer (SQL):**
   * SQLite table schema initialized with `CHECK` constraints (`price_gbp >= 0`, `rating BETWEEN 1 AND 5`).
   * Compound indexing (`idx_books_rating_price`) on heavily queried aggregation columns for $O(\log N)$ search speed.
   * Batch insertions performed via multi-row parameterized SQL queries.

4. **Testing & Code Quality:**
   * Full unit testing coverage using `pytest`.
   * Standard Python Type Hinting and Google-style docstrings across all modules.

---

## 📊 Database Schema Definition

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL CHECK(price_gbp >= 0),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    in_stock BOOLEAN NOT NULL CHECK(in_stock IN (0, 1)),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_rating_price ON books(rating, price_gbp);
```

## 🚀 Getting Started

1. **Prerequisite Installation**
    * Ensure you have Python 3.9+ installed. Clone the repository and set up dependencies:


    * git clone [https://github.com/YOUR-USERNAME/price-intelligence-pipeline.git](https://github.com/YOUR-USERNAME/price-intelligence-pipeline.git)
    cd price-intelligence-pipeline

    * Create and activate virtual environment
    python -m venv venv
    source venv/bin/activate # On Windows use: venv\Scripts\activate

    * Install dependencies
    pip install -r requirements.txt

2. **Execution Sequence**
    * Run the complete pipeline end-to-end:


    * 1. Execute Extraction Scraper
    python scraper.py

    * 2. Execute Transformation and Database Load
    python cleaner.py

    * 3. Generate Analytical Report
    python analysis.py

3. **Run Unit Test Suite**
    * To verify pipeline stability and execution assertions:

    pytest test_pipeline.py -v


## 📝 Logging & Observability

All operational events, network failures, data drop counts, and execution metrics are logged simultaneously to the console and a local persistent file: pipeline.log.

Example log output:

Plaintext
2026-08-03 17:55:01,120 - INFO - Initializing scraper pipeline for 5 pages.
2026-08-03 17:55:02,450 - INFO - Successfully extracted 20 items from page 1
2026-08-03 17:55:08,110 - INFO - Database schema initialized and indices created successfully.
2026-08-03 17:55:08,230 - INFO - Successfully inserted 100 rec