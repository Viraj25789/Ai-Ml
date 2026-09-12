"""
RetailIQ — a small retail analytics platform.

Tabs:
1. Dashboard        — KPIs & charts over the retail dataset
2. Ask Your Data     — type a business question in plain English, the app
                       retrieves the closest matching SQL report (a small,
                       honest form of retrieval — no external API required)
                       and runs it live
3. Customer Segments — RFM analysis + KMeans clustering (basic ML)
4. SQL Playground     — write and run your own SQL against the same database

Run locally:  streamlit run app.py
"""
import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from query_library import QUERY_LIBRARY

DB_PATH = "retailiq.db"

# On a fresh deploy (e.g. Streamlit Community Cloud) the .db file may not be
# in the repo — build it on first run so there's nothing manual to set up.
if not os.path.exists(DB_PATH):
    import seed_data
    seed_data.build()

st.set_page_config(page_title="RetailIQ", page_icon="📊", layout="wide")


@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def run_query(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_connection())


@st.cache_resource
def build_retriever():
    """Fit a TF-IDF vectorizer over the 60 saved query descriptions.
    This is the 'retrieval' half of retrieval-augmented search: instead of
    generating SQL from scratch (which needs an LLM + a lot more guardrails),
    we retrieve the closest hand-verified, already-correct query. It's simple,
    transparent, costs nothing to run, and never produces a wrong/unsafe query.
    """
    corpus = [f"{q['question']} {q.get('keywords', '')}" for q in QUERY_LIBRARY]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix


# A small cache of very common phrasings, checked before falling back to the
# vector search. This mirrors how real retrieval systems handle frequent
# queries: cheap exact/substring lookups first, semantic search as the safety net.
FAQ_SHORTCUTS = {
    "top customers": "Q44", "best customers": "Q44", "highest spending customer": "Q44",
    "low stock": "Q6", "running low": "Q6", "restock": "Q6",
    "revenue by month": "Q49", "monthly revenue": "Q49", "sales trend": "Q49",
    "best employee": "Q45", "top employee": "Q45", "top salesperson": "Q45",
    "top selling category": "Q48", "best category": "Q48", "most popular category": "Q48",
    "customers who never ordered": "Q34", "inactive customers": "Q34",
    "products that never sold": "Q35", "dead stock": "Q35", "unsold products": "Q35",
    "top products": "Q40", "best selling products": "Q40", "bestsellers": "Q40",
    "second highest price": "Q51", "second highest salary": "Q53",
    "customers who spend more than average": "Q57", "big spenders": "Q57",
}


def find_best_match(user_question: str, top_k: int = 3):
    normalized = user_question.strip().lower()

    shortcut_hit = None
    for phrase, qid in sorted(FAQ_SHORTCUTS.items(), key=lambda kv: -len(kv[0])):
        if phrase in normalized:
            shortcut_hit = qid
            break

    vectorizer, matrix = build_retriever()
    user_vec = vectorizer.transform([user_question])
    sims = cosine_similarity(user_vec, matrix).flatten()
    top_idx = sims.argsort()[::-1][:top_k]
    results = [(QUERY_LIBRARY[i], float(sims[i])) for i in top_idx]

    if shortcut_hit:
        shortcut_query = next(q for q in QUERY_LIBRARY if q["id"] == shortcut_hit)
        results = [(shortcut_query, 0.99)] + [r for r in results if r[0]["id"] != shortcut_hit]

    return results[:top_k]


# ---------------------------------------------------------------------------
st.title("📊 RetailIQ")
st.caption("A small analytics platform over a synthetic Indian electronics-retail dataset.")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Dashboard", "💬 Ask Your Data", "🧩 Customer Segments", "🛠️ SQL Playground"]
)

# ---------------------------------------------------------------------------
# TAB 1 — Dashboard
# ---------------------------------------------------------------------------
with tab1:
    kpi_sql = """
    SELECT
        (SELECT COUNT(*) FROM customers) AS customers,
        (SELECT COUNT(*) FROM orders) AS orders,
        (SELECT ROUND(SUM(quantity * unit_price * (1 - discount)), 0) FROM order_items) AS revenue,
        (SELECT ROUND(AVG(quantity * unit_price * (1 - discount)), 0)
            FROM (SELECT quantity, unit_price, discount, order_id FROM order_items) oi
        ) AS avg_item_value
    """
    kpis = run_query(kpi_sql).iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", f"{int(kpis.customers):,}")
    c2.metric("Total Orders", f"{int(kpis.orders):,}")
    c3.metric("Total Revenue", f"₹{int(kpis.revenue):,}")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        monthly = run_query("""
            SELECT strftime('%Y-%m', o.order_date) AS month,
                   SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
            FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY month ORDER BY month
        """)
        fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly Revenue")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        by_category = run_query("""
            SELECT cat.category_name,
                   SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories cat ON p.category_id = cat.category_id
            GROUP BY cat.category_name ORDER BY revenue DESC
        """)
        fig2 = px.bar(by_category, x="category_name", y="revenue", title="Revenue by Category")
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        top_products = run_query("""
            SELECT p.product_name,
                   SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_name ORDER BY revenue DESC LIMIT 10
        """)
        fig3 = px.bar(top_products, x="revenue", y="product_name", orientation="h",
                      title="Top 10 Products by Revenue")
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        payment_split = run_query("""
            SELECT payment_method, COUNT(*) AS orders
            FROM orders GROUP BY payment_method
        """)
        fig4 = px.pie(payment_split, names="payment_method", values="orders",
                      title="Orders by Payment Method")
        st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2 — Ask Your Data (retrieval-based NL search)
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Ask a business question in plain English")
    st.caption(
        "This searches a library of 60 hand-written, verified SQL reports and "
        "runs the closest match — a lightweight, transparent form of retrieval. "
        "Try: *'who are my top customers'*, *'which products are low on stock'*, "
        "*'revenue by month'*."
    )

    user_q = st.text_input("Your question", placeholder="e.g. which category sells the most?")

    if user_q:
        matches = find_best_match(user_q, top_k=3)
        best_match, best_score = matches[0]

        if best_score < 0.15:
            st.warning("No confident match found in the query library — try rephrasing.")
        else:
            st.success(f"Closest match: **{best_match['question']}**  (similarity: {best_score:.2f})")
            with st.expander("Show the SQL that ran"):
                st.code(best_match["sql"], language="sql")

            result = run_query(best_match["sql"])
            st.dataframe(result, use_container_width=True)

            if result.shape[1] == 2 and result.shape[0] > 1 and result.shape[0] <= 30:
                numeric_col = result.select_dtypes(include="number").columns
                label_col = [c for c in result.columns if c not in numeric_col]
                if len(numeric_col) and len(label_col):
                    fig = px.bar(result, x=label_col[0], y=numeric_col[0])
                    st.plotly_chart(fig, use_container_width=True)

            if len(matches) > 1:
                with st.expander("Other close matches"):
                    for m, score in matches[1:]:
                        st.write(f"- {m['question']}  (similarity: {score:.2f})")

# ---------------------------------------------------------------------------
# TAB 3 — Customer Segmentation (basic ML: RFM + KMeans)
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Customer Segmentation (RFM + KMeans)")
    st.caption(
        "Classic Recency–Frequency–Monetary analysis, clustered with KMeans. "
        "Useful for a marketing team deciding who to target with which campaign."
    )

    rfm_sql = """
    SELECT c.customer_id, c.customer_name,
           julianday('2026-01-01') - julianday(MAX(o.order_date)) AS recency_days,
           COUNT(DISTINCT o.order_id) AS frequency,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name
    """
    rfm = run_query(rfm_sql)

    n_clusters = st.slider("Number of segments", 2, 6, 4)

    features = rfm[["recency_days", "frequency", "monetary"]]
    scaled = StandardScaler().fit_transform(features)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm["segment"] = km.fit_predict(scaled)

    segment_summary = rfm.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_recency_days=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
    ).round(1).reset_index()

    st.dataframe(segment_summary, use_container_width=True)

    fig = px.scatter(
        rfm, x="frequency", y="monetary", color=rfm["segment"].astype(str),
        size="recency_days", hover_data=["customer_name"],
        title="Customer Segments (bubble size = days since last order)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Segments with low recency, high frequency, and high monetary value are your "
        "best customers — a good starting point for a loyalty campaign."
    )

# ---------------------------------------------------------------------------
# TAB 4 — SQL Playground
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Write your own SQL")
    st.caption("Runs directly against the same SQLite database. SELECT statements only.")

    default_query = "SELECT * FROM customers LIMIT 10;"
    query_text = st.text_area("SQL query", value=default_query, height=150)

    if st.button("Run query"):
        if not query_text.strip().lower().startswith("select") and \
           not query_text.strip().lower().startswith("with"):
            st.error("Only SELECT / WITH queries are allowed in the playground.")
        else:
            try:
                result = run_query(query_text)
                st.dataframe(result, use_container_width=True)
                st.caption(f"{len(result)} rows returned.")
            except Exception as e:
                st.error(f"Query failed: {e}")

    with st.expander("Browse the 60 practiced queries"):
        for q in QUERY_LIBRARY:
            st.markdown(f"**{q['id']}. {q['question']}**")
            st.code(q["sql"], language="sql")
