
import logging
import os
from typing import Optional

import pandas as pd

from database import DatabaseManager


logger = logging.getLogger(__name__)


class DataCleaner:
    """Validate, clean, and prepare scraped book data for analysis."""

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    REQUIRED_COLUMNS = ["Title", "Price", "Rating", "Stock_Status"]

    def __init__(
        self,
        raw_data_path: str = "data/raw_books.csv",
        clean_data_path: str = "data/clean_books.csv",
    ):
        self.raw_data_path = raw_data_path
        self.clean_data_path = clean_data_path
        self.db_manager = DatabaseManager()

    def load_raw_data(self) -> Optional[pd.DataFrame]:
        """Load raw CSV data if the source file exists."""
        if not os.path.exists(self.raw_data_path):
            logger.error("Raw data file not found: %s", self.raw_data_path)
            return None

        try:
            df = pd.read_csv(self.raw_data_path)
            logger.info("Loaded %s raw records.", len(df))
            return df
        except (OSError, pd.errors.ParserError, UnicodeError) as error:
            logger.exception("Could not read raw CSV: %s", error)
            return None

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean fields and remove records that violate data rules."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        clean_df = df[self.REQUIRED_COLUMNS].copy()
        initial_count = len(clean_df)

        # Standardize text fields.
        clean_df["Title"] = clean_df["Title"].astype("string").str.strip()

        # Convert currency strings into numeric prices.
        price_text = (
            clean_df["Price"]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.replace(r"[^\d.\-]", "", regex=True)
        )
        clean_df["Price"] = pd.to_numeric(price_text, errors="coerce")

        # Convert rating labels into integers.
        rating_text = clean_df["Rating"].astype("string").str.strip()
        clean_df["Rating"] = (
            rating_text.map(self.RATING_MAP)
            .fillna(pd.to_numeric(rating_text, errors="coerce"))
        )

        # Convert inventory status into a boolean.
        stock_text = (
            clean_df["Stock_Status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )
        clean_df["In_Stock"] = stock_text.str.startswith("in stock")

        # Remove missing, malformed, and out-of-range records.
        valid_records = (
            clean_df["Title"].notna()
            & clean_df["Title"].ne("")
            & clean_df["Price"].notna()
            & clean_df["Price"].ge(0)
            & clean_df["Rating"].notna()
            & clean_df["Rating"].between(1, 5)
        )

        clean_df = clean_df.loc[valid_records].copy()

        clean_df["Rating"] = clean_df["Rating"].astype(int)
        clean_df["In_Stock"] = clean_df["In_Stock"].astype(bool)

        clean_df = clean_df[
            ["Title", "Price", "Rating", "In_Stock"]
        ].reset_index(drop=True)

        removed_count = initial_count - len(clean_df)

        logger.info(
            "Data cleaning complete: %s valid records retained, "
            "%s invalid records removed.",
            len(clean_df),
            removed_count,
        )

        return clean_df

    def process_and_save(self) -> Optional[pd.DataFrame]:
        """Run the cleaning, CSV export, and database loading steps."""
        raw_df = self.load_raw_data()

        if raw_df is None or raw_df.empty:
            logger.error("ETL stopped: no source records available.")
            return None

        try:
            clean_df = self.transform(raw_df)

            if clean_df.empty:
                logger.error("ETL stopped: no valid records after cleaning.")
                return None

            os.makedirs(
                os.path.dirname(self.clean_data_path) or ".",
                exist_ok=True,
            )
            clean_df.to_csv(self.clean_data_path, index=False)

            logger.info(
                "Clean dataset exported: %s",
                self.clean_data_path,
            )

            if self.db_manager.save_dataframe(clean_df):
                logger.info("Database loading completed.")
            else:
                logger.error("Database loading failed.")

            return clean_df

        except (ValueError, TypeError, OSError) as error:
            logger.exception("ETL processing failed: %s", error)
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cleaner = DataCleaner()
    cleaner.process_and_save()
