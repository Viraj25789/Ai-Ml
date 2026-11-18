"""
llm_sql.py
An LLM-powered fallback for questions that don't match anything in the
60-query library. Kept in its own module so the safety rules are easy to
audit in one place.

Uses Groq's free API tier (fast Llama models, no card required) via plain
HTTP — no extra SDK dependency. Requires a GROQ_API_KEY, read via
Streamlit secrets or an environment variable. If no key is configured this
whole feature quietly disables itself; the rest of the app works fine
without it.

Get a free key: https://console.groq.com/keys
"""
import os
import re
import requests

GROQ_MODEL = "openai/gpt-oss-20b"
# Tried in order; if one is retired/unavailable for the account, the next is
# used automatically. Groq periodically deprecates model names, so this list
# is worth revisiting occasionally — check https://console.groq.com/docs/models
FALLBACK_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "groq/compound-mini"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SCHEMA_DESCRIPTION = """
Tables (SQLite):

customers(customer_id, customer_name, city, state, customer_type, signup_date)
  -- customer_type is one of: 'Premium', 'Regular', 'New'
products(product_id, product_name, category_id, supplier, price, stock, rating)
categories(category_id, category_name)
employees(employee_id, employee_name, department, salary, hire_date)
orders(order_id, customer_id, employee_id, order_date, payment_method)
order_items(order_item_id, order_id, product_id, quantity, unit_price, discount)
  -- revenue for a line item = quantity * unit_price * (1 - discount)
"""

SYSTEM_PROMPT = f"""You are a SQLite expert. Given a database schema and a
business question, write exactly one SQLite SELECT query that answers it.

Schema:
{SCHEMA_DESCRIPTION}

Rules:
- Output ONLY the raw SQL query. No explanation, no markdown code fences, no comments.
- Use only SELECT or WITH ... SELECT. Never modify data.
- Use only the tables and columns listed above.
- End the query without a trailing semicolon.
"""

# Anything beyond a single read-only SELECT gets rejected before it ever
# touches the database, regardless of what the model returns.
FORBIDDEN_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|REPLACE|VACUUM|GRANT)\b",
    re.IGNORECASE,
)


def get_api_key() -> str | None:
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")


def is_safe_select(sql: str) -> tuple[bool, str]:
    """Returns (is_safe, reason_if_not)."""
    cleaned = sql.strip().rstrip(";").strip()
    if not cleaned:
        return False, "Empty query."
    if ";" in cleaned:
        return False, "Multiple statements are not allowed."
    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        return False, "Only SELECT / WITH queries are allowed."
    if FORBIDDEN_PATTERN.search(cleaned):
        return False, "Query contains a disallowed keyword."
    return True, ""


def clean_sql_output(raw: str) -> str:
    """Strip markdown fences etc. in case the model ignores instructions."""
    text = raw.strip()
    text = re.sub(r"^```(sql)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text.rstrip(";").strip()


def _call_groq(api_key: str, model: str, question: str) -> str:
    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "temperature": 0,
            "max_tokens": 300,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate_sql(question: str) -> str:
    """Calls the LLM and returns a cleaned SQL string. Tries each model in
    FALLBACK_MODELS in order in case one has been deprecated on the account —
    Groq retires model names more often than most providers. Raises only if
    every candidate fails (missing key, network error, all models unavailable)."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "No GROQ_API_KEY configured. Add a free key from "
            "https://console.groq.com/keys to your Streamlit secrets."
        )

    last_error = None
    for model in FALLBACK_MODELS:
        try:
            raw_sql = _call_groq(api_key, model, question)
            return clean_sql_output(raw_sql)
        except requests.exceptions.HTTPError as e:
            last_error = e
            if e.response is not None and e.response.status_code == 404:
                continue  # model unavailable on this account — try the next one
            raise
    raise RuntimeError(
        f"All configured Groq models failed (last error: {last_error}). "
        "Check https://console.groq.com/docs/models for currently available models."
    )
