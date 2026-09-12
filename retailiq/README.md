# RetailIQ

A small analytics platform built on top of a synthetic Indian electronics-retail
dataset (customers, products, categories, employees, orders). I built this after
working through ~60 SQL practice questions (basic filtering → aggregation → joins
→ business questions → interview-level window functions/subqueries) — instead of
leaving them as a folder of `.sql` files, I turned them into an actual product:
a dashboard, a natural-language query tool, and a basic ML feature.

**Live demo:** _add your Streamlit Cloud link here once deployed_
**SQL practice write-up:** see [`queries/`](./queries) — all 60 queries, organized
by difficulty level, each one commented with the original question.

## What's in it

| Tab | What it does |
|---|---|
| 📈 Dashboard | KPIs + charts: monthly revenue, revenue by category, top 10 products, payment method split |
| 💬 Ask Your Data | Type a question in plain English ("who are my top customers?") and it retrieves the closest matching SQL report from a library of 60 hand-verified queries and runs it live |
| 🧩 Customer Segments | RFM (Recency/Frequency/Monetary) analysis + KMeans clustering to group customers into segments |
| 🛠️ SQL Playground | Write and run your own `SELECT` queries against the same database, or browse all 60 practiced queries |

## Why "Ask Your Data" isn't a black box

I didn't want to fake an LLM-powered text-to-SQL feature and call it "AI" — that's
brittle and honestly kind of dishonest for a portfolio piece. What it actually does
is simpler and more defensible: it uses TF-IDF + cosine similarity to find the
closest matching query from a curated library of 60 already-correct, already-tested
SQL statements, with a small lookup table for the most common phrasings ("top
customers", "low stock", etc.) checked first. It's the retrieval half of RAG,
applied to a case where "generation" would just mean re-deriving queries I already
wrote and verified. No API key needed, nothing can break in production, and it's
genuinely explainable if an interviewer asks "how does this work" — which I'd
actually recommend leading with, because it shows you understand the tradeoffs
instead of just bolting on a buzzword.

## Project structure

```
retailiq/
├── app.py                  # Streamlit app (all 4 tabs)
├── schema.sql               # Database schema
├── seed_data.py              # Generates the synthetic dataset -> retailiq.db
├── query_library.py           # The 60 queries + descriptions, used by "Ask Your Data"
├── queries/
│   ├── level1_basic.sql
│   ├── level2_aggregation.sql
│   ├── level3_joins.sql
│   ├── level4_business.sql
│   └── level5_challenge.sql
├── requirements.txt
└── README.md
```

## Running it locally

```bash
git clone https://github.com/<your-username>/retailiq.git
cd retailiq
pip install -r requirements.txt
python seed_data.py        # builds retailiq.db (~650 orders, 220 customers)
streamlit run app.py
```

It'll open at `http://localhost:8501`.

## Deploying it for free

**Streamlit Community Cloud** (easiest, no card required):
1. Push this repo to GitHub (make sure `retailiq.db` is either committed, or
   have Streamlit run `seed_data.py` on startup — I do the latter, see the
   note in `app.py`).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Pick this repo, set the main file to `app.py`, deploy.
4. Takes about 2 minutes to spin up. Free tier is enough for a portfolio demo.

**Alternative:** Render.com's free web service tier also works — set the
start command to `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

## What I'd add next

- Swap the synthetic dataset for a real one (Kaggle has a few decent retail
  datasets) to talk about data cleaning in interviews too.
- Add a proper text-to-SQL layer using a small local LLM for queries that
  don't fit the existing library — with a validator that only allows `SELECT`
  and blocks anything that touches schema or other tables, before I'd trust it
  in front of a real database.
- Cache the RFM computation instead of recomputing it on every slider change.

## Tech

Python, SQLite, Streamlit, Plotly, scikit-learn (KMeans, TF-IDF).
