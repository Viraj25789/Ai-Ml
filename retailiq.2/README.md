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
| 💬 Ask Your Data | Type a question in plain English. First checks a library of 60 hand-verified SQL reports for a close match; if nothing fits, an LLM (Groq, free tier) writes a fresh query on the spot — so you're not limited to the 60 questions I originally practiced |
| 🧩 Customer Segments | RFM (Recency/Frequency/Monetary) analysis + KMeans clustering to group customers into segments |
| 🛠️ SQL Playground | Write and run your own `SELECT` queries against the same database, or browse all 60 practiced queries |

## Why "Ask Your Data" is retrieval-first, not LLM-first

The library of 60 queries is checked before the model ever gets called. If
there's a confident match, that's what runs — it's already tested, it's
free, and it can't hallucinate a wrong column name. The LLM only writes a
new query when nothing in the library fits, or if you explicitly ask it to
try again. That's a genuine hybrid retrieval-augmented pattern, not just a
chatbot wrapper, and it's a distinction worth bringing up if an interviewer
asks how the feature works.

**Guardrails on the LLM path**, since letting a model generate SQL against a
real database is exactly the kind of thing that goes wrong if you're not
careful:
- The model is only ever asked for a single `SELECT` — the prompt says so explicitly
- Before running anything, the generated SQL is checked against a blocklist
  (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `ATTACH`, `PRAGMA`, etc.)
  and rejected if it contains more than one statement
- As a second line of defense, LLM-generated and playground queries run
  against a SQLite connection opened in **read-only mode** — even a query
  that somehow got past the filter physically cannot write to the database

### Enabling the AI fallback

The app works fully without this — it just won't offer AI-generated queries
beyond the 60 built-ins. To turn it on:

1. Get a free key at [console.groq.com/keys](https://console.groq.com/keys) (no card needed)
2. Locally: copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   and paste your key in
3. On Streamlit Community Cloud: go to your app → **Settings → Secrets** and add:
   ```toml
   GROQ_API_KEY = "your-key-here"
   ```

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
- Log every LLM-generated query (question, SQL, whether it succeeded) so I
  can see where it struggles and fold the good ones back into the library —
  turning the fallback into a feedback loop instead of a one-shot guess.
- Cache the RFM computation instead of recomputing it on every slider change.

## Tech

Python, SQLite, Streamlit, Plotly, scikit-learn (KMeans, TF-IDF).
