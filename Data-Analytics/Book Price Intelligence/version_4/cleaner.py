import os
import logging
import pandas as pd
from typing import Optional
from database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

class DataCleaner:
    """
    Production-grade ETL Transformer that ingests raw extracted CSV data,
    applies cleaning routines, enforces domain constraints, and exports clean datasets.
    """

    RATING_MAP = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }

    def __init__(self, raw_data_path: str = "data/raw_books.csv", clean_data_path: str = "data/clean_books.csv"):
        self.raw_data_path = raw_data_path
        self.clean_data_path = clean_data_path
        self.db_manager = DatabaseManager()

    def load_raw_data(self) -> Optional[pd.DataFrame]:
        """Loads raw dataset with file validation."""
        if not os.path.exists(self.raw_data_path):
            logging.error(f"Target raw file not found at path: {self.raw_data_path}")
            return None

        try:
            df = pd.read_csv(self.raw_data_path)
            logging.info(f"Loaded raw dataset containing {len(df)} records.")
            return df
        except Exception as e:
            logging.error(f"Failed to read raw CSV file: {e}")
            return None

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes pure functional transformations on the DataFrame.
        """
        clean_df = df.copy()

        # 1. Clean Price Column
        logging.info("Transforming price attributes to numeric float format...")
        clean_df['Price'] = (
            clean_df['Price']
            .astype(str)
            .str.replace(r'[^\d.]', '', regex=True) # Defensive regex extraction for numeric and decimal points
            .astype(float)
        )

        # 2. Map Ordinal String Ratings to Integers
        logging.info("Mapping rating categories to numerical values...")
        clean_df['Rating'] = clean_df['Rating'].map(self.RATING_MAP).fillna(0).astype(int)

        # 3. Clean and Standardize Inventory Status to Boolean Flag
        logging.info("Normalizing stock availability into boolean representation...")
        clean_df['In_Stock'] = (
            clean_df['Stock_Status']
            .astype(str)
            .str.contains('In stock', case=False, regex=False)
            .astype(bool)
        )

        # Drop legacy raw columns
        clean_df.drop(columns=['Stock_Status'], inplace=True, errors='ignore')

        # 4. Data Quality Audit
        initial_count = len(clean_df)
        clean_df.dropna(subset=['Title', 'Price', 'Rating'], inplace=True)
        dropped_count = initial_count - len(clean_df)
        
        if dropped_count > 0:
            logging.warning(f"Data Quality Check: Dropped {dropped_count} invalid records due to null values.")

        return clean_df

    def process_and_save(self) -> Optional[pd.DataFrame]:
        """Runs the complete transformation workflow and persists output."""
        raw_df = self.load_raw_data()
        if raw_df is None or raw_df.empty:
            logging.error("ETL Transformation aborted: No valid source data available.")
            return None

        clean_df = self.transform(raw_df)

        # File Persistence
        try:
            clean_df.to_csv(self.clean_data_path, index=False)
            logging.info(f"Clean dataset exported successfully to CSV: {self.clean_data_path}")
        except Exception as e:
            logging.error(f"Failed to save clean CSV: {e}")

        # SQL Database Persistence
        db_success = self.db_manager.save_dataframe(clean_df)
        if db_success:
            logging.info("Clean dataset successfully loaded into relational SQLite database.")

        return clean_df


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.process_and_save()