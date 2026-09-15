# RetailIQ

A small analytics platform built on top of a retail dataset (customers,
products, categories, employees, orders). I built this after working
through ~60 SQL practice questions (basic filtering → aggregation → joins
→ business questions → interview-level window functions/subqueries) —
instead of leaving them as a folder of `.sql` files, I turned them into an
actual product: a live dashboard, a natural-language query tool, a real
Postgres backend option, and a basic ML feature.

**Live demo:** _add your Streamlit Cloud link here once deployed_
**SQL practice write-up:** see [`queries/`](./queries) — all 60 queries, organized
by difficulty level, each one commented with the original question.

## What's in it

| Tab | What it does |
|---|---|
| 📈 Dashboard | KPIs + charts, plus a "Live" toggle that simulates a new incoming order every 15 seconds against the real database |
| 💬 Ask Your Data | Type a question in plain English. First checks a library of 60 hand-verified SQL reports for a close match; if nothing fits, an LLM (Groq, free tier) writes a fresh query on the spot |
| 🧩 Customer Segments | RFM (Recency/Frequency/Monetary) analysis + KMeans clustering to group customers into segments |
| 🛠️ SQL Playground | Write and run your own `SELECT` queries against the same database, or browse all 60 practiced queries |

## Two ways to run it

By default this runs on a local SQLite file — zero setup, works the moment
you `pip install` and run it. Set a `DATABASE_URL` secret and it switches to
a real, shared, persistent **Postgres** database instead, with no code
changes needed anywhere else. This matters for a portfolio project: a local
SQLite file resets every time the app restarts, which is fine for a demo
but doesn't show you can work against a real, concurrent, persistent store.

### Running on local SQLite (default, no setup)

```bash
git clone https://github.com/<your-username>/retailiq.git
cd retailiq
pip install -r requirements.txt
python seed_data.py        # builds retailiq.db (~650 orders, 220 customers)
streamlit run app.py
```

### Connecting a real Postgres database (free)

1. Create a free Postgres instance at [neon.com](https://neon.com) or
   [supabase.com](https://supabase.com) — both have a genuinely free tier,
   no card required. Copy the connection string they give you.
2. Set it as a secret:
   - Locally: copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
     and paste it in as `DATABASE_URL`
   - On Streamlit Community Cloud: app → **Settings → Secrets**:
     ```toml
     DATABASE_URL = "postgresql://user:password@host/dbname"
     ```
3. Run the app — it detects the secret, creates the schema, and seeds it
   automatically on first run. Every visitor after that shares the same
   live database.
4. **Recommended extra step:** run [`setup_readonly_role.sql`](./setup_readonly_role.sql)
   once against your database (Neon and Supabase both have a SQL editor in
   their dashboard) to create a role that can only ever `SELECT`. Set the
   resulting connection string as a second secret, `DATABASE_URL_READONLY`.
   This is what the "Ask Your Data" LLM path and the SQL Playground run
   against — so even if a bad query somehow got past the app-level
   validation, the database itself would refuse to let it write anything.
   I tested this for real (created the role, tried an `INSERT` and a `DROP`
   against it, both correctly rejected with `permission denied`) rather than
   just assuming Postgres grants work the way I expected.

The same query code runs against either backend — a `db.py` module resolves
a couple of SQL functions that aren't spelled the same way in SQLite and
Postgres (month bucketing, day-difference calculations) rather than
hardcoding SQLite syntax everywhere.

## "Live" mode

The Dashboard tab has a toggle that inserts one new synthetic order every
15 seconds using [`streamlit-autorefresh`](https://pypi.org/project/streamlit-autorefresh/).
It's honest about what it is: since there's no real point-of-sale system to
connect to, this simulates order flow rather than pretending to have one.
What *is* real is that it's writing to and reading from an actual shared
database in real time — on Postgres, if you open the app in two browser
tabs, both see the same incrementing numbers, which is a genuinely useful
thing to be able to talk through in an interview (concurrent reads/writes,
connection pooling, autocommit behavior).

One bug worth mentioning because I hit it while building this: my first
version of the order-insert used a plain read-style connection for an
`INSERT ... RETURNING` statement. It never committed, so the follow-up
insert (the order's line items) ran in a separate transaction that couldn't
see the new order yet, and failed on the foreign key. Fixed by committing
the insert-and-return-id as one transaction (`db.run_insert_returning`).

## Using a real dataset instead of synthetic data

`load_real_data.py` replaces the synthetic generator with the well-known
"Superstore Sales" dataset (5,496 real orders, 795 customers, 1,263
products, spanning 2009–2012) — fetched directly from a public GitHub
mirror, no Kaggle login needed:

```bash
python load_real_data.py
```

This is genuine ETL, not just loading a CSV: the source is one flat table
(one row per order line) and has to be split into the schema's six
normalized tables. Some things worth being upfront about if you present
this in an interview:

- Customers, products, categories, orders, dates, quantities, prices, and
  discounts are all real, from the source data.
- The source has **no employee/salesperson field** — the script generates
  a small placeholder staff list and assigns orders to them randomly, only
  so the schema's foreign key has something to point to. Don't present
  "which employee sold the most" as a real insight on this dataset.
- The source has no true payment-method field either, only a shipping mode
  (Regular Air / Delivery Truck / Express Air) — stored in the
  `payment_method` column since the schema doesn't distinguish them. It's
  shipping data wearing a different column name.
- A couple of the 60 library queries filter on values that only exist in
  the synthetic generator (e.g. `customer_type = 'Premium'`) — the real
  dataset uses different segment names (`Corporate`, `Consumer`, etc.), so
  those specific queries will return empty results until you adjust the
  filter value. Run `SELECT DISTINCT customer_type FROM customers` to see
  what's actually there before assuming a query is broken.

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
- As a second line of defense, both the LLM path and the SQL Playground run
  against a connection that's read-only at the database level — a SQLite
  connection opened in read-only URI mode, or (on Postgres) a dedicated
  role with `SELECT`-only grants. Even a query that somehow got past the
  keyword filter physically cannot write.

### Enabling the AI fallback

The app works fully without this — it just won't offer AI-generated queries
beyond the 60 built-ins. To turn it on:

1. Get a free key at [console.groq.com/keys](https://console.groq.com/keys) (no card needed)
2. Add it as a secret the same way as `DATABASE_URL` above:
   ```toml
   GROQ_API_KEY = "your-key-here"
   ```

Groq periodically retires model names — `llm_sql.py` tries a short list of
fallback models in order (`FALLBACK_MODELS`) rather than hardcoding just
one, so a single deprecation doesn't break the feature outright. If it ever
stops working entirely, check [console.groq.com/docs/models](https://console.groq.com/docs/models)
for the current list and update that list.

## Project structure

```
retailiq/
├── app.py                    # Streamlit app (all 4 tabs)
├── db.py                     # SQLite/Postgres connection layer + dialect-aware SQL helpers
├── theme.py                  # Design system (CSS + Plotly styling)
├── llm_sql.py                 # LLM fallback for "Ask Your Data" + safety validation
├── schema.sql                # Database schema (SQLite)
├── schema_postgres.sql        # Database schema (Postgres)
├── seed_data.py               # Generates the synthetic dataset
├── load_real_data.py          # Loads the real Superstore dataset instead
├── setup_readonly_role.sql    # One-time script to create a read-only Postgres role
├── query_library.py           # The 60 queries + descriptions, used by "Ask Your Data"
├── queries/
│   ├── level1_basic.sql
│   ├── level2_aggregation.sql
│   ├── level3_joins.sql
│   ├── level4_business.sql
│   └── level5_challenge.sql
├── requirements.txt
├── runtime.txt
└── README.md
```

## Deploying it for free

**Streamlit Community Cloud** (easiest, no card required):
1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Pick this repo, set the main file to `app.py`. If using Postgres, add
   your secrets first (see above).
4. Deploy. Takes a few minutes to spin up on first build (installing
   scikit-learn/psycopg2 isn't instant) — that's normal, not stuck.

**Alternative:** Render.com's free web service tier also works — set the
start command to `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

## What I'd add next

- Log every LLM-generated query (question, SQL, whether it succeeded) so I
  can see where it struggles and fold the good ones back into the library —
  turning the fallback into a feedback loop instead of a one-shot guess.
- Cache the RFM computation instead of recomputing it on every slider change.
- A proper background job for "live" data instead of piggybacking on the
  page's own reruns — Streamlit Cloud's free tier doesn't run background
  workers, so right now new orders only arrive while someone has the
  Live toggle on and the tab open.

## Tech

Python, SQLAlchemy, SQLite/Postgres, Streamlit, Plotly, scikit-learn
(KMeans, TF-IDF), Groq (LLM fallback).
