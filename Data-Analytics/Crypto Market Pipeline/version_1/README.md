# Live Crypto Market Pipeline (Version 1)

A foundational data engineering pipeline that extracts live financial data from a REST API, flattens nested JSON structures, and performs automated market sentiment analysis.

## 🚀 Overview
This project demonstrates core API interaction and data structuring techniques:
1. **Extraction:** Connects to the CoinGecko public API via HTTP GET requests.
2. **Flattening:** Uses Pandas `json_normalize` to convert deeply nested JSON (like Return-On-Investment dictionaries) into a structured 2D DataFrame.
3. **Analysis:** Calculates market sentiment, top gainers, and top losers using live data.

## ⚙️ How to Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt

2. **Run the pipeline**
    ```bash
   # Extract live JSON and flatten to CSV
    python api_extractor.py

    # Run market analytics
    python api_analyzer.py