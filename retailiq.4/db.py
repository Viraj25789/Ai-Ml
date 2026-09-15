"""
db.py — connects RetailIQ to either a local SQLite file or a cloud Postgres
database, using the same query code either way.

Why this exists: the original version was SQLite-only, which is fine for a
portfolio demo but doesn't show you can work against a real, shared,
persistent database. Add a `DATABASE_URL` secret (e.g. a free Neon or
Supabase Postgres instance) and the app switches over automatically — no
code changes needed elsewhere. Without one, it keeps using a local SQLite
file, so the project still works out of the box for anyone who clones it.

A couple of SQL functions (month bucketing, day differences) aren't spelled
the same way in SQLite and Postgres, so this module also exposes small
dialect-aware helpers (`month_expr`, `days_since_expr`) that the handful of
queries needing them call into, rather than hardcoding SQLite syntax
everywhere.
"""
import os
from sqlalchemy import create_engine, text
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "retailiq.db")


def get_database_url() -> str:
    """Looks for a DATABASE_URL secret/env var (a Postgres connection
    string). Falls back to a local SQLite file if none is set."""
    url = None
    try:
        import streamlit as st
        url = st.secrets.get("DATABASE_URL")
    except Exception:
        pass
    url = url or os.environ.get("DATABASE_URL")

    if url:
        # SQLAlchemy wants the psycopg2 dialect spelled out; most hosted
        # Postgres providers (Neon, Supabase, Railway) hand you a plain
        # "postgresql://..." or "postgres://..." string.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    return f"sqlite:///{SQLITE_PATH}"


_engine = None
_readonly_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = get_database_url()
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    return _engine


def get_readonly_engine():
    """Uses a DATABASE_URL_READONLY secret if one is configured (recommended
    for Postgres — see README for the one-time SQL to create a read-only
    role). Falls back to the main engine if no separate URL is set, since
    on SQLite the connection itself is opened read-only elsewhere anyway."""
    global _readonly_engine
    if _readonly_engine is None:
        url = None
        try:
            import streamlit as st
            url = st.secrets.get("DATABASE_URL_READONLY")
        except Exception:
            pass
        url = url or os.environ.get("DATABASE_URL_READONLY")

        if url:
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            _readonly_engine = create_engine(url, pool_pre_ping=True)
        else:
            _readonly_engine = get_engine()
    return _readonly_engine


def is_postgres() -> bool:
    return get_engine().dialect.name == "postgresql"


def using_sqlite() -> bool:
    return get_engine().dialect.name == "sqlite"


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params)


def run_query_readonly(sql: str, params: dict | None = None) -> pd.DataFrame:
    """For SQL that didn't come from our own verified library — LLM output,
    the playground. On SQLite this opens a connection in read-only URI mode
    (physically cannot write, regardless of query content). On Postgres it
    uses DATABASE_URL_READONLY if configured (a role with SELECT-only
    grants — see README); otherwise it falls back to the main connection,
    relying on the keyword/statement validation in llm_sql.is_safe_select."""
    if using_sqlite():
        import sqlite3
        uri = f"file:{SQLITE_PATH}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            return pd.read_sql_query(sql, conn, params=params)
        finally:
            conn.close()
    with get_readonly_engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params)


def run_statement(sql: str, params: dict | None = None):
    """For INSERT/UPDATE — used only by our own seeding/simulation code,
    never by user- or LLM-supplied SQL."""
    with get_engine().begin() as conn:
        conn.execute(text(sql), params or {})


def run_insert_returning(sql: str, params: dict, returning_col: str):
    """Like run_statement, but for an INSERT ... RETURNING that needs the
    generated value back (e.g. a new order's ID) before the transaction
    commits. Using a plain SELECT-style connection for this was the original
    bug here: it never committed, so a follow-up insert in a separate
    transaction couldn't see the new row yet and failed on the foreign key."""
    with get_engine().begin() as conn:
        result = conn.execute(text(sql), params)
        row = result.fetchone()
        return row._mapping[returning_col] if row is not None else None


def executescript(sql_script: str):
    """Runs a multi-statement DDL script (schema creation). Splits on ';'
    since SQLAlchemy's text() doesn't run multiple statements per call."""
    statements = [s.strip() for s in sql_script.split(";") if s.strip()]
    with get_engine().begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))


# ---------------------------------------------------------------------------
# Dialect-aware SQL fragments
# ---------------------------------------------------------------------------

def month_expr(date_column: str) -> str:
    """Returns a SQL fragment that buckets a date column into 'YYYY-MM'."""
    if is_postgres():
        return f"TO_CHAR({date_column}, 'YYYY-MM')"
    return f"strftime('%Y-%m', {date_column})"


def days_since_expr(date_column: str, reference_literal: str = "CURRENT_DATE") -> str:
    """Returns a SQL fragment for (reference_date - date_column) in days."""
    if is_postgres():
        return f"EXTRACT(DAY FROM ({reference_literal}::timestamp - {date_column}::timestamp))"
    ref = "julianday('now')" if reference_literal == "CURRENT_DATE" else f"julianday({reference_literal})"
    return f"({ref} - julianday({date_column}))"


def autoincrement_pk(name: str = "id") -> str:
    """Primary key column definition, dialect-aware."""
    if is_postgres():
        return f"{name} SERIAL PRIMARY KEY"
    return f"{name} INTEGER PRIMARY KEY"
