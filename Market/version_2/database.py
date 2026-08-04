import sqlite3
import pandas as pd
import logging
from typing import Optional

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_pipeline.log"),
        logging.StreamHandler()
    ]
)

class CryptoDatabase:
    """Manages SQLite connections and schema for live financial data."""

    def __init__(self, db_path: str = "data/crypto_market.db"):
        self.db_path = db_path
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_schema(self) -> None:
        """Creates the historical market data table with a timestamp."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            current_price REAL NOT NULL,
            market_cap REAL NOT NULL,
            price_change_24h REAL NOT NULL,
            roi_percentage REAL,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self._get_connection() as conn:
                conn.execute(create_table_sql)
            logging.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize database schema: {e}")

    def save_dataframe(self, df: pd.DataFrame) -> bool:
        """Persists the flattened JSON data directly into the SQL database."""
        if df.empty:
            logging.warning("Empty DataFrame provided. Skipping insertion.")
            return False

        # Map Pandas columns to SQL schema names
        rename_map = {
            'name': 'asset_name',
            'symbol': 'symbol',
            'current_price': 'current_price',
            'market_cap': 'market_cap',
            'price_change_percentage_24h': 'price_change_24h',
            'roi.percentage': 'roi_percentage'
        }
        formatted_df = df.rename(columns=rename_map)

        try:
            with self._get_connection() as conn:
                formatted_df.to_sql(
                    name='market_data',
                    con=conn,
                    if_exists='append', # Append to keep historical data
                    index=False
                )
            logging.info(f"Successfully inserted {len(formatted_df)} records into SQLite.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database insertion failed: {e}")
            return False
            
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Executes a read query and returns a DataFrame."""
        try:
            with self._get_connection() as conn:
                return pd.read_sql_query(query, conn)
        except sqlite3.Error as e:
            logging.error(f"SQL execution error: {e}")
            return None