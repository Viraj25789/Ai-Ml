import sqlite3
import pandas as pd
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

class DatabaseManager:
    """
    Manages SQLite database connections, schema migrations, and high-performance
    batch insertions for the e-commerce data pipeline.
    """

    def __init__(self, db_path: str = "data/ecommerce_catalog.db"):
        self.db_path = db_path
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates and returns a new database connection."""
        return sqlite3.connect(self.db_path)

    def _initialize_schema(self) -> None:
        """
        Creates the target relational table and indices if they do not exist.
        Includes constraints to ensure data integrity at the database level.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL CHECK(price_gbp >= 0),
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            in_stock BOOLEAN NOT NULL CHECK(in_stock IN (0, 1)),
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Indexing frequently queried analytical columns
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_books_rating_price 
        ON books(rating, price_gbp);
        """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                cursor.execute(create_index_sql)
                conn.commit()
            logging.info("Database schema initialized and indices created successfully.")
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize database schema: {e}")
            raise

    def save_dataframe(self, df: pd.DataFrame, table_name: str = "books", if_exists: str = "append") -> bool:
        """
        Persists a cleaned Pandas DataFrame directly into the SQL database.
        
        Args:
            df (pd.DataFrame): Cleaned DataFrame with aligned schema columns.
            table_name (str): Target database table name.
            if_exists (str): Action if table exists ('fail', 'replace', 'append').
            
        Returns:
            bool: True if transaction succeeded, False otherwise.
        """
        if df.empty:
            logging.warning("Received empty DataFrame. Skipping database insertion.")
            return False

        # Rename columns to match SQL schema conventions
        rename_map = {
            'Title': 'title',
            'Price': 'price_gbp',
            'Rating': 'rating',
            'In_Stock': 'in_stock'
        }
        
        formatted_df = df.rename(columns=rename_map)
        
        # Filter for schema alignment
        target_columns = ['title', 'price_gbp', 'rating', 'in_stock']
        formatted_df = formatted_df[target_columns]

        try:
            with self._get_connection() as conn:
                formatted_df.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists=if_exists,
                    index=False,
                    method='multi', # Vectorized batch insertion
                    chunksize=500
                )
                conn.commit()
            logging.info(f"Successfully inserted {len(formatted_df)} records into '{table_name}' table.")
            return True
        except (sqlite3.Error, Exception) as e:
            logging.error(f"Database insertion failed: {e}")
            return False

    def execute_query(self, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
        """Executes a read query and returns the result as a Pandas DataFrame."""
        try:
            with self._get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except sqlite3.Error as e:
            logging.error(f"SQL execution error: {e}")
            return None


if __name__ == "__main__":
    db = DatabaseManager()
    logging.info("Database manager module execution completed.")