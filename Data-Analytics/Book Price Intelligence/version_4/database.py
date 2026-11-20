import logging
import math
import os
import sqlite3
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage the SQLite database for the book price pipeline."""

    def __init__(self, db_path: str = "data/ecommerce_catalog.db"):
        self.db_path = db_path
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a database connection and its parent directory."""
        directory = os.path.dirname(self.db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _initialize_schema(self) -> None:
        """Create the books table and analytical index."""
        connection = self._get_connection()
        try:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        price_gbp REAL NOT NULL CHECK(price_gbp >= 0),
                        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                        in_stock BOOLEAN NOT NULL CHECK(in_stock IN (0, 1)),
                        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                connection.execute("""
                    CREATE INDEX IF NOT EXISTS idx_books_rating_price
                    ON books(rating, price_gbp)
                """)
            logger.info("Database schema initialized.")
        finally:
            connection.close()

    def save_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str = "books",
    ) -> bool:
        """Replace records only after every incoming row passes validation."""
        if table_name != "books":
            logger.error("Unsupported table: %s", table_name)
            return False
        if not isinstance(df, pd.DataFrame) or df.empty:
            logger.warning("Empty or invalid DataFrame. Database unchanged.")
            return False

        required_columns = ["Title", "Price", "Rating", "In_Stock"]
        missing = [column for column in required_columns if column not in df.columns]
        if missing:
            logger.error("Missing columns: %s", ", ".join(missing))
            return False

        try:
            records = []
            for title, price, rating, in_stock in df[required_columns].itertuples(
                index=False, name=None
            ):
                if pd.isna(title) or pd.isna(price) or pd.isna(rating) or pd.isna(in_stock):
                    raise ValueError("Dataset contains missing required values.")

                title = str(title).strip()
                price = float(price)
                rating_value = float(rating)

                # Do not silently truncate fractional ratings or accept infinities.
                if (
                    not title
                    or not math.isfinite(price)
                    or price < 0
                    or not math.isfinite(rating_value)
                    or not rating_value.is_integer()
                    or int(rating_value) not in range(1, 6)
                ):
                    raise ValueError("Dataset contains invalid book records.")

                # bool and numeric 0/1 are accepted; strings such as "False"
                # are rejected instead of being treated as True by bool(...).
                if isinstance(in_stock, str):
                    raise ValueError("Stock status must be a boolean or 0/1.")
                stock_value = float(in_stock)
                if not math.isfinite(stock_value) or stock_value not in (0.0, 1.0):
                    raise ValueError("Stock status must be a boolean or 0/1.")

                records.append((title, price, int(rating_value), int(stock_value)))

            connection = self._get_connection()
            try:
                with connection:
                    connection.execute("DELETE FROM books")
                    connection.executemany(
                        """
                        INSERT INTO books
                            (title, price_gbp, rating, in_stock)
                        VALUES (?, ?, ?, ?)
                        """,
                        records,
                    )
            finally:
                connection.close()

            logger.info(
                "Database refreshed successfully with %s records.", len(records)
            )
            return True
        except (sqlite3.Error, ValueError, TypeError, OverflowError):
            logger.exception("Database refresh failed.")
            return False

    def execute_query(
        self,
        query: str,
        params: tuple = (),
    ) -> Optional[pd.DataFrame]:
        """Execute a SQL query and return its results as a DataFrame."""
        connection = self._get_connection()
        try:
            return pd.read_sql_query(query, connection, params=params)
        except (sqlite3.Error, pd.errors.DatabaseError):
            logger.exception("SQL execution failed.")
            return None
        finally:
            connection.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    database = DatabaseManager()
    logger.info("Database manager initialized successfully.")
