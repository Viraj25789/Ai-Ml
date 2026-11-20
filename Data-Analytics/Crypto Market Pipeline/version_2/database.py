import logging
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


logger = logging.getLogger(__name__)


class CryptoDatabase:
    """Stores and queries historical cryptocurrency market snapshots."""

    REQUIRED_COLUMNS = {
        "name",
        "symbol",
        "current_price",
        "market_cap",
        "price_change_percentage_24h",
    }

    COLUMN_MAPPING = {
        "name": "asset_name",
        "symbol": "symbol",
        "current_price": "current_price",
        "market_cap": "market_cap",
        "price_change_percentage_24h": "price_change_24h",
        "roi.percentage": "roi_percentage",
    }

    def __init__(self, db_path: str = "data/crypto_market.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection with foreign-key checks enabled."""
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_schema(self) -> None:
        """Create the market history table and useful indexes."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            current_price REAL NOT NULL CHECK (current_price >= 0),
            market_cap REAL NOT NULL CHECK (market_cap >= 0),
            price_change_24h REAL NOT NULL,
            roi_percentage REAL,
            extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self._get_connection() as connection:
                connection.execute(create_table_sql)
                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_market_data_extracted_at
                    ON market_data (extracted_at)
                    """
                )
                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_market_data_symbol
                    ON market_data (symbol)
                    """
                )
        except sqlite3.Error:
            logger.exception("Could not initialize the market database.")
            raise

    def save_dataframe(self, df: pd.DataFrame) -> bool:
        """Validate and append one market snapshot to the history table."""
        if not isinstance(df, pd.DataFrame) or df.empty:
            logger.warning("No market data supplied; skipping database insert.")
            return False

        missing_columns = self.REQUIRED_COLUMNS.difference(df.columns)
        if missing_columns:
            logger.error("Market data is missing columns: %s", sorted(missing_columns))
            return False

        available_columns = [
            column for column in self.COLUMN_MAPPING if column in df.columns
        ]
        cleaned = df[available_columns].copy()
        cleaned = cleaned.rename(columns=self.COLUMN_MAPPING)

        for column in ("current_price", "market_cap", "price_change_24h", "roi_percentage"):
            if column in cleaned.columns:
                cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

        cleaned["asset_name"] = cleaned["asset_name"].astype("string").str.strip()
        cleaned["symbol"] = cleaned["symbol"].astype("string").str.strip().str.lower()

        required_numeric = ["current_price", "market_cap", "price_change_24h"]
        cleaned = cleaned.dropna(
            subset=["asset_name", "symbol", *required_numeric]
        )
        cleaned = cleaned[
            (cleaned["asset_name"] != "")
            & (cleaned["symbol"] != "")
            & (cleaned["current_price"] >= 0)
            & (cleaned["market_cap"] >= 0)
        ]

        if cleaned.empty:
            logger.warning("No valid market records remain after validation.")
            return False

        cleaned = cleaned.reindex(
            columns=[
                "asset_name",
                "symbol",
                "current_price",
                "market_cap",
                "price_change_24h",
                "roi_percentage",
            ]
        )
        cleaned = cleaned.astype(object).where(pd.notna(cleaned), None)

        insert_sql = """
        INSERT INTO market_data (
            asset_name, symbol, current_price, market_cap,
            price_change_24h, roi_percentage
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """

        try:
            records = list(cleaned.itertuples(index=False, name=None))
            with self._get_connection() as connection:
                connection.executemany(insert_sql, records)
            logger.info("Inserted %s valid market records.", len(records))
            return True
        except (sqlite3.Error, ValueError, TypeError):
            logger.exception("Failed to save market data.")
            return False

    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Run a read-only SQL query and return its results as a DataFrame."""
        if not isinstance(query, str) or not query.strip():
            logger.error("A non-empty SQL query is required.")
            return None

        statement = query.lstrip().lower()
        if not (statement.startswith("select") or statement.startswith("with")):
            logger.error("Only read-only SELECT queries are allowed.")
            return None

        try:
            with self._get_connection() as connection:
                connection.execute("PRAGMA query_only = ON")
                return pd.read_sql_query(query, connection)
        except (sqlite3.Error, pd.errors.DatabaseError):
            logger.exception("SQL query failed.")
            return None
