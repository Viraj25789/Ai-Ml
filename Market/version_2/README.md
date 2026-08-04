# Enterprise REST API Pipeline

A resilient data engineering microservice that extracts live financial JSON data from a REST API, flattens the nested structures, and persists the payload into a relational database.

## 🚀 System Architecture
This Version 2 upgrade transitions from a functional script to a production-ready system:
* **Object-Oriented Design:** Modular classes for database management, API extraction, and analysis.
* **Resilient Networking:** Implements HTTP Session pooling, explicit timeout constraints, and `HTTP 429 (Rate Limit)` exception handling.
* **Relational Storage:** Migrates data storage from flat CSV files to an SQLite database (`data/crypto_market.db`), tracking historical extraction timestamps.
* **JSON Normalization:** Utilizes Pandas `json_normalize` to automatically unnest complex dictionary payloads.

## ⚙️ How to Run

1. **Install dependencies**
   ```bash
   pip install requests pandas

2. **Execute the pipeline**
    ```bash
    python api_pipeline.py
    python api_analyzer.py