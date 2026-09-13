"""
RetailIQ — a small retail analytics platform.

Tabs:
1. Dashboard        — KPIs & charts over the retail dataset
2. Ask Your Data     — type a business question in plain English, the app
                       retrieves the closest matching SQL report (a small,
                       honest form of retrieval), falling back to an LLM
                       for questions the library doesn't cover
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
import llm_sql
import theme

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "retailiq.db")

# On a fresh deploy (e.g. Streamlit Community Cloud) the .db file may not be
# in the repo — build it on first run so there's nothing manual to set up.
if not os.path.exists(DB_PATH):
    import seed_data
    seed_data.build()

st.set_page_config(page_title="RetailIQ", page_icon="🗒️", layout="wide")
theme.inject()


@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_resource
def get_readonly_connection():
    """A connection opened in SQLite's read-only URI mode — used for any SQL
    that didn't come from our own verified query library (LLM output, the
    playground). Even if a bad query slipped past the keyword filter, the
    database itself would refuse to let it write anything."""
    uri = f"file:{DB_PATH}?mode=ro"
    return sqlite3.connect(uri, uri=True, check_same_thread=False)


def run_query(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_connection())


def run_query_readonly(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_readonly_connection())


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

EXAMPLE_QUESTIONS = [
    "who are my top customers",
    "which products are low on stock",
    "revenue by month",
    "best selling category",
]


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
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### RetailIQ")
    st.caption("A ledger, made interactive.")
    st.markdown(
        "Built on a synthetic Indian electronics-retail dataset — "
        "220 customers, 30 products, 650 orders."
    )
    st.divider()
    st.markdown("**Stack**")
    st.caption("Python · SQLite · Streamlit · scikit-learn · Groq")
    st.divider()
    st.markdown("**Source**")
    st.caption("Add your GitHub link here once pushed.")

# ---------------------------------------------------------------------------
theme.masthead("RetailIQ", "Analytics over a small electronics retail business.")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Dashboard", "Ask Your Data", "Customer Segments", "SQL Playground"]
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

    theme.kpi_row([
        ("Customers", f"{int(kpis.customers):,}"),
        ("Orders", f"{int(kpis.orders):,}"),
        ("Revenue", f"₹{int(kpis.revenue):,}"),
        ("Avg. line value", f"₹{int(kpis.avg_item_value):,}"),
    ])

    col_a, col_b = st.columns(2)

    with col_a:
        monthly = run_query("""
            SELECT strftime('%Y-%m', o.order_date) AS month,
                   SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
            FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY month ORDER BY month
        """)
        fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly revenue")
        st.plotly_chart(theme.apply_chart_style(fig), use_container_width=True)

    with col_b:
        by_category = run_query("""
            SELECT cat.category_name,
                   SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN categories cat ON p.category_id = cat.category_id
            GROUP BY cat.category_name ORDER BY revenue DESC
        """)
        fig2 = px.bar(by_category, x="category_name", y="revenue", title="Revenue by category")
        st.plotly_chart(theme.apply_chart_style(fig2), use_container_width=True)

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
                      title="Top 10 products by revenue")
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(theme.apply_chart_style(fig3), use_container_width=True)

    with col_d:
        payment_split = run_query("""
            SELECT payment_method, COUNT(*) AS orders
            FROM orders GROUP BY payment_method
        """)
        fig4 = px.pie(payment_split, names="payment_method", values="orders",
                      title="Orders by payment method")
        st.plotly_chart(theme.apply_chart_style(fig4), use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2 — Ask Your Data (retrieval-based NL search, LLM fallback)
# ---------------------------------------------------------------------------
with tab2:
    theme.section_label(
        "Checks a library of 60 verified reports first. "
        "Falls back to an AI-generated query if nothing fits."
    )

    if "riq_input" not in st.session_state:
        st.session_state.riq_input = ""

    chip_cols = st.columns(len(EXAMPLE_QUESTIONS))
    for col, example in zip(chip_cols, EXAMPLE_QUESTIONS):
        with col:
            st.markdown('<div class="riq-chip">', unsafe_allow_html=True)
            if st.button(example, key=f"chip_{example}", use_container_width=True):
                st.session_state.riq_input = example
            st.markdown('</div>', unsafe_allow_html=True)

    user_q = st.text_input(
        "Your question",
        placeholder="e.g. which category sells the most?",
        key="riq_input",
    )

    if user_q:
        matches = find_best_match(user_q, top_k=3)
        best_match, best_score = matches[0]
        CONFIDENT_THRESHOLD = 0.35

        if best_score >= CONFIDENT_THRESHOLD:
            st.markdown(f"**Closest match** · {best_match['question']}  ·  similarity {best_score:.2f}")
            with st.expander("Show the SQL that ran"):
                st.code(best_match["sql"], language="sql")

            result = run_query(best_match["sql"])
            st.dataframe(result, use_container_width=True)

            if result.shape[1] == 2 and result.shape[0] > 1 and result.shape[0] <= 30:
                numeric_col = result.select_dtypes(include="number").columns
                label_col = [c for c in result.columns if c not in numeric_col]
                if len(numeric_col) and len(label_col):
                    fig = px.bar(result, x=label_col[0], y=numeric_col[0])
                    st.plotly_chart(theme.apply_chart_style(fig, height=320), use_container_width=True)

            if len(matches) > 1:
                with st.expander("Other close matches"):
                    for m, score in matches[1:]:
                        st.write(f"- {m['question']}  ·  similarity {score:.2f}")

            st.divider()
            ask_ai_anyway = st.toggle("Not what you meant? Ask the AI model instead")
        else:
            st.markdown(
                "Nothing in the 60-query library matches this closely. "
                "Ask the AI model below, or try one of the example questions above."
            )
            ask_ai_anyway = True

        if ask_ai_anyway:
            api_key = llm_sql.get_api_key()
            if not api_key:
                st.warning(
                    "AI fallback isn't configured yet. Add a free `GROQ_API_KEY` "
                    "(get one at console.groq.com/keys) to your Streamlit secrets "
                    "to enable open-ended questions beyond the 60 built-ins."
                )
            else:
                with st.spinner("Writing a query for that..."):
                    try:
                        generated_sql = llm_sql.generate_sql(user_q)
                        safe, reason = llm_sql.is_safe_select(generated_sql)
                    except Exception as e:
                        st.error(f"Couldn't reach the model: {e}")
                        safe = False
                        generated_sql = ""

                if generated_sql and not safe:
                    st.error(f"Generated query was rejected for safety: {reason}")
                    st.code(generated_sql, language="sql")
                elif generated_sql:
                    st.markdown("**AI-generated** · verify before relying on it")
                    st.code(generated_sql, language="sql")
                    try:
                        ai_result = run_query_readonly(generated_sql)
                        st.dataframe(ai_result, use_container_width=True)
                    except Exception as e:
                        st.error(f"The generated query failed to run: {e}")

# ---------------------------------------------------------------------------
# TAB 3 — Customer Segmentation (basic ML: RFM + KMeans)
# ---------------------------------------------------------------------------
with tab3:
    theme.section_label(
        "Recency, frequency, and monetary value, clustered with KMeans — "
        "a starting point for deciding who to target with which campaign."
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
        title="Customer segments — bubble size is days since last order"
    )
    st.plotly_chart(theme.apply_chart_style(fig, height=460), use_container_width=True)

    st.caption(
        "Segments with low recency, high frequency, and high monetary value are the "
        "best customers — a starting point for a loyalty campaign."
    )

# ---------------------------------------------------------------------------
# TAB 4 — SQL Playground
# ---------------------------------------------------------------------------
with tab4:
    theme.section_label("Runs directly against the database. SELECT statements only.")

    default_query = "SELECT * FROM customers LIMIT 10;"
    query_text = st.text_area("SQL query", value=default_query, height=150)

    if st.button("Run query"):
        if not query_text.strip().lower().startswith("select") and \
           not query_text.strip().lower().startswith("with"):
            st.error("Only SELECT / WITH queries run here.")
        else:
            try:
                result = run_query_readonly(query_text)
                st.dataframe(result, use_container_width=True)
                st.caption(f"{len(result)} rows returned.")
            except Exception as e:
                st.error(f"Query failed: {e}")

    with st.expander("Browse the 60 practiced queries"):
        for q in QUERY_LIBRARY:
            st.markdown(f"**{q['id']}. {q['question']}**")
            st.code(q["sql"], language="sql")
