# Market Basket & Product Recommendation System

A Flask dashboard that analyzes retail transaction baskets and generates product and customer recommendations. It combines association-rule mining, user-based collaborative filtering, and a lightweight next-purchase sequence model.

## Business problem

Retailers want to understand which products are purchased together, recommend relevant products to customers, and identify frequently and infrequently purchased items. This project demonstrates those analyses using transaction-level CSV data.

## Features

- **Frequently bought together:** association rules using support, confidence, and lift.
- **Product bundles:** ranks useful product combinations.
- **Personalized recommendations:** user-based collaborative filtering with cosine similarity.
- **New-user fallback:** recommends popular products when a customer has no known purchase history.
- **Next-purchase suggestions:** a first-order Markov transition model based on each customer's ordered transaction history.
- **Customer and market summary:** transaction counts, unique users, basket size, product frequency, and a downloadable text report.
- **Dataset upload:** accepts a CSV with the required transaction columns.

## How it works

1. Load transaction data from a CSV file.
2. Split each row's comma-separated `Items` into a basket.
3. Calculate product co-occurrence and association-rule metrics.
4. Build a user-item matrix and calculate user similarity.
5. Build per-user purchase transitions for next-item suggestions.
6. Display the results in a Flask dashboard.

## Technology

- Python
- Flask and Jinja2
- pandas and NumPy
- scikit-learn (cosine similarity)
- HTML, CSS, JavaScript, Chart.js
- Optional TensorFlow module for experimental sequence modelling

## Project structure

```text
The Market Basket And Bucket Recommendation System/
├── app.py
├── generate_dataset.py
├── model/
│   ├── apriori_model.py
│   ├── collaborative_filtering.py
│   └── lstm_prediction.py
├── templates/
│   └── index.html
├── static/
│   ├── charts.js
│   └── style.css
├── data/
│   └── default.csv
├── requirements.txt
└── README.md
```

## Dataset format

The CSV must contain:

| Column | Required | Description |
|---|---|---|
| `TransactionID` | Recommended | Transaction sequence / identifier |
| `UserID` | Yes | Customer identifier |
| `Items` | Yes | Comma-separated products in the basket |

Example (the basket must be quoted because it contains commas):


```csv
TransactionID,UserID,Items
1,101,"Laptop, Mouse"
2,101,"Keyboard, Mouse"
3,102,"Smartphone, Headphones"
```

Column names are case-insensitive. The app accepts `UserID`, `user_id`, or `user` as the customer column.

## Run locally

Clone the repository:

```bash
git clone https://github.com/Viraj25789/Ai-Ml.git
cd Ai-Ml
cd "Recommendation Systems/The Market Basket And Bucket Recommendation System"
```

Create and activate a virtual environment:

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

Install dependencies and start the application:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

For deployment, set the `FLASK_SECRET_KEY` environment variable and run the app with a production WSGI server such as Gunicorn. The built-in Flask server is for local development only.

## Generate sample data

To generate a synthetic 5,000-transaction dataset:

```bash
python generate_dataset.py
```

The script writes `transactions_5000.csv` to the current working directory. Move it into the `data/` folder or upload it through the dashboard.

## Important notes and limitations

- The uploaded dataset is stored locally under `data/`; use trusted CSV files only.
- Association rules and recommendations depend on transaction quality and volume. Sparse data may produce few or no useful rules.
- The customer churn-risk label is a simple heuristic based on purchase counts, not a trained churn prediction model.
- The Markov next-item output is a pattern-based suggestion, not a calibrated probability of future purchase.
- The optional LSTM module is experimental and is not part of the default dashboard workflow.
- This is a portfolio / learning project, not a production retail recommendation service.

## Author

**Viraj Parmar** · [GitHub](https://github.com/Viraj25789)
