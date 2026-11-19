# RetailIQ — Retail Analytics Platform

RetailIQ is a Python-based retail analytics application built using a synthetic Indian electronics retail dataset.

It helps explore business performance, ask questions about retail data using SQL, and identify customer groups using RFM analysis and KMeans clustering.

## Features

### 1. Business Dashboard
- Total customers and orders
- Revenue overview
- Monthly revenue trends
- Revenue by product category
- Top products by revenue
- Payment method distribution

### 2. Ask Your Data
Ask business questions in natural language.

The application:
- Searches a library of predefined SQL queries first.
- Uses TF-IDF similarity to find relevant queries.
- Can use a Groq language model as an optional SQL-generation fallback.
- Executes generated queries using a read-only SQLite connection.

Example questions:
- Who are my top customers?
- Which products have low stock?
- What is the monthly revenue?
- Which category generates the most revenue?

### 3. Customer Segmentation
Uses RFM analysis:

- **Recency:** How recently a customer placed an order.
- **Frequency:** How often a customer placed orders.
- **Monetary:** How much a customer spent.

KMeans clustering groups customers based on these three measures.

### 4. SQL Playground
- Run custom SQL queries.
- Explore the retail database.
- Browse the predefined SQL query collection.
- Supports read-only SELECT queries.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data Analysis | Pandas, NumPy |
| Database | SQLite |
| Dashboard | Streamlit |
| Visualisation | Plotly |
| Machine Learning | scikit-learn |
| Text Retrieval | TF-IDF, cosine similarity |
| AI Integration | Groq API |

## Project Structure

```text
retailiq_4/
│
├── app.py
├── seed_data.py
├── schema.sql
├── query_library.py
├── llm_sql.py
├── theme.py
├── requirements.txt
├── README.md
│
└── queries/
    ├── level1_basic.sql
    ├── level2_aggregation.sql
    ├── level3_joins.sql
    ├── level4_business.sql
    └── level5_challenge.sql
```

## Dataset

This project uses synthetically generated retail data.

The generator creates:
- 220 customers
- 30 products
- 18 employees
- 650 orders
- Multiple order items per order

The dataset includes customer details, product information, order dates, payment methods, quantities and discounts.

**Note:** This is sample data for demonstration and learning. It does not represent actual business transactions.

## Installation and Setup

### Requirements

- Python 3.10 or newer recommended
- pip
- Git

### Step 1: Clone the repository

```bash
git clone https://github.com/Viraj25789/Ai-Ml.git
```

### Step 2: Open the RetailIQ folder

```bash
cd Ai-Ml/Data-Analytics/RetailIQ/retailiq_4
```

### Step 3: Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Generate the database

```bash
python seed_data.py
```

This creates the SQLite database using the schema and synthetic data generator.

### Step 6: Run the application

```bash
streamlit run app.py
```

Open the local address displayed in your terminal, usually:

```text
http://localhost:8501
```

## Optional: Enable AI-generated SQL

The application can use a Groq API key for questions that do not match the predefined SQL query library.

1. Create an API key from [Groq Console](https://console.groq.com/keys).
2. Set the `GROQ_API_KEY` environment variable.

Windows PowerShell:

```powershell
$env:GROQ_API_KEY="your-api-key"
```

3. Start the application in the same terminal:

```bash
streamlit run app.py
```

Never upload your API key to GitHub or commit it inside a source file.

The dashboard, predefined SQL queries, customer segmentation and SQL playground can be explored without configuring the optional AI service.


## Automated Testing

RetailIQ includes automated tests using Python's built-in `unittest` framework.

### Run tests locally

From the `retailiq_4` directory:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test coverage

The automated test suite checks:

- All 60 saved SQL queries are available.
- Saved SQL queries pass safety validation.
- All saved SQL queries execute successfully.
- Database record counts match expected values.
- Unsafe SQL statements are rejected.
- No orphan records exist in the database.
- Foreign-key integrity is maintained.
- Existing databases are protected from accidental overwrites.

GitHub Actions automatically runs the test suite on pushes and pull requests.


## Important Notes

- The database is generated locally when it does not exist.
- The data is synthetic and intended for demonstration.
- AI-generated SQL may not always answer a question correctly.
- Verify generated queries and their results before using them for business decisions.
- The project is a portfolio and learning application, not a production retail management system.

## Future Improvements

- Add automated tests for SQL queries and data processing.
- Improve customer segment descriptions.
- Add more data quality checks.
- Improve AI-generated SQL validation.
- Add project screenshots and a verified live demo.

## Author

**Viraj Parmar**

GitHub: [Viraj25789](https://github.com/Viraj25789)
