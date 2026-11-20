# Crypto Market Data Pipeline

A Python data engineering project that collects cryptocurrency market data from the CoinGecko public API, validates and transforms the response, stores historical snapshots in SQLite, and generates a market summary.

## What the project does

1. **Extracts data** from CoinGecko's markets endpoint using HTTP requests, timeouts, and retry handling.
2. **Validates and transforms data** with pandas, including nested ROI fields and invalid records.
3. **Stores snapshots** in SQLite using parameterized SQL inserts.
4. **Creates a CSV backup** using a temporary file and atomic replacement.
5. **Analyzes the latest snapshot** to identify the top gainer, top loser, average 24-hour change, and overall market direction.
6. **Runs automated tests** for the pipeline, storage, and analysis logic.

## Architecture

```text
CoinGecko API
     |
     v
api_pipeline.py
     |
     +--> Validate and transform (pandas)
     |
     +--> data/latest_market_data.csv
     |
     +--> database.py --> data/crypto_market.db
                              |
                              v
                       api_analyzer.py
                              |
                              v
                       Market summary
```

## Tech stack

- Python 3.11+
- requests
- pandas
- SQLite
- pytest
- GitHub Actions

## Project structure

```text
version_2/
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/                  # Generated database and CSV backup
├── tests/
│   └── test_crypto_pipeline.py
├── api_pipeline.py        # API extraction and transformation
├── api_analyzer.py        # Latest market snapshot analysis
├── database.py            # SQLite schema and persistence
├── requirements.txt
└── README.md
```

## Setup

Clone the repository and open this project directory:

```bash
git clone https://github.com/Viraj25789/Ai-Ml.git
cd Ai-Ml
cd "Data-Analytics/Crypto Market Pipeline/version_2"
```

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Run the pipeline

First collect and store a market snapshot:

```bash
python api_pipeline.py
```

Then generate a report from the latest stored snapshot:

```bash
python api_analyzer.py
```

The first command creates the `data/` directory and writes the SQLite database and CSV backup. These are generated locally and are excluded from version control.

## Run tests

```bash
pytest -v
```

GitHub Actions also runs the test suite when files in this project are changed.

## Database

The `market_data` table stores:

| Column | Description |
|---|---|
| asset_name | Cryptocurrency name |
| symbol | Trading symbol |
| current_price | Current price in USD |
| market_cap | Market capitalization in USD |
| price_change_24h | Percentage change over 24 hours |
| roi_percentage | Return on investment percentage, when available |
| extracted_at | Snapshot timestamp |

Each successful extraction appends a new snapshot, preserving historical records.

## Notes and limitations

- Data availability and request limits are controlled by CoinGecko.
- The project uses the public API endpoint and does not require an API key for basic use.
- Market sentiment is a simple average of the assets' 24-hour percentage changes; it is an educational summary, not investment advice.
- Historical snapshots are collected only when the pipeline is run.

## Author

**Viraj Parmar**

GitHub: [Viraj25789](https://github.com/Viraj25789)
