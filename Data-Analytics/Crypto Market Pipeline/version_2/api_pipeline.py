
import logging
import math
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from database import CryptoDatabase


logger = logging.getLogger(__name__)


class CoinGeckoPipeline:
    """Extract, validate, and store cryptocurrency market data."""

    BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"

    REQUIRED_API_FIELDS = [
        "name",
        "symbol",
        "current_price",
        "market_cap",
        "price_change_percentage_24h",
    ]

    OUTPUT_COLUMNS = [
        "name",
        "symbol",
        "current_price",
        "market_cap",
        "price_change_percentage_24h",
        "roi.percentage",
    ]

    def __init__(
        self,
        db: Optional[CryptoDatabase] = None,
        output_path: str = "data/latest_market_data.csv",
        timeout: tuple = (5, 20),
    ):
        self.base_url = self.BASE_URL
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.db = db or CryptoDatabase()

        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_api_data(self) -> Optional[List[Dict]]:
        """Fetch market data and validate the API response structure."""

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "sparkline": False,
        }

        try:
            logger.info("Requesting cryptocurrency market data.")

            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list):
                logger.error("Unexpected API response: expected a list.")
                return None

            if not data:
                logger.warning("The API returned an empty dataset.")
                return None

            valid_records = [
                record for record in data if isinstance(record, dict)
            ]

            if not valid_records:
                logger.error("The API response contains no valid records.")
                return None

            logger.info("Received %s API records.", len(valid_records))
            return valid_records

        except requests.exceptions.HTTPError as exc:
            logger.error("CoinGecko HTTP error: %s", exc)
        except requests.exceptions.RequestException as exc:
            logger.error("CoinGecko network error: %s", exc)
        except ValueError as exc:
            logger.error("Could not decode API JSON response: %s", exc)

        return None

    def process_data(self, raw_json: List[Dict]) -> Optional[pd.DataFrame]:
        """Normalize API records and remove invalid market data."""

        if not isinstance(raw_json, list) or not raw_json:
            logger.warning("No valid API records supplied.")
            return None

        records = [
            record for record in raw_json if isinstance(record, dict)
        ]

        if not records:
            logger.warning("No dictionary records found in API response.")
            return None

        try:
            df = pd.json_normalize(records)

            missing_fields = set(self.REQUIRED_API_FIELDS) - set(df.columns)
            if missing_fields:
                logger.error(
                    "API data is missing required fields: %s",
                    sorted(missing_fields),
                )
                return None

            for column in self.OUTPUT_COLUMNS:
                if column not in df.columns:
                    df[column] = None

            clean_df = df[self.OUTPUT_COLUMNS].copy()

            numeric_columns = [
                "current_price",
                "market_cap",
                "price_change_percentage_24h",
                "roi.percentage",
            ]

            for column in numeric_columns:
                clean_df[column] = pd.to_numeric(
                    clean_df[column],
                    errors="coerce",
                )

            clean_df["name"] = clean_df["name"].astype("string").str.strip()
            clean_df["symbol"] = (
                clean_df["symbol"].astype("string").str.strip().str.lower()
            )

            required_columns = [
                "current_price",
                "market_cap",
                "price_change_percentage_24h",
            ]

            valid_rows = (
                clean_df["name"].notna()
                & clean_df["symbol"].notna()
                & (clean_df["name"] != "")
                & (clean_df["symbol"] != "")
            )

            for column in required_columns:
                valid_rows &= clean_df[column].map(
                    lambda value: pd.notna(value)
                    and math.isfinite(float(value))
                )

            clean_df = clean_df.loc[valid_rows].copy()

            clean_df = clean_df[
                (clean_df["current_price"] >= 0)
                & (clean_df["market_cap"] >= 0)
            ]

            if clean_df.empty:
                logger.error("No valid market records remain after cleaning.")
                return None

            logger.info(
                "Validated %s of %s market records.",
                len(clean_df),
                len(records),
            )

            return clean_df.reset_index(drop=True)

        except (KeyError, TypeError, ValueError) as exc:
            logger.exception("Market data processing failed: %s", exc)
            return None

    def save_csv_backup(self, df: pd.DataFrame) -> bool:
        """Write a CSV backup safely without replacing it on failure."""

        if not isinstance(df, pd.DataFrame) or df.empty:
            logger.warning("CSV backup skipped: no data available.")
            return False

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                suffix=".tmp",
                prefix="market_data_",
                dir=self.output_path.parent,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                df.to_csv(temporary_file, index=False)

            os.replace(temporary_path, self.output_path)

            logger.info("CSV backup saved to %s.", self.output_path)
            return True

        except (OSError, ValueError) as exc:
            logger.exception("Could not save CSV backup: %s", exc)

            if temporary_path and temporary_path.exists():
                try:
                    temporary_path.unlink()
                except OSError:
                    logger.warning(
                        "Could not remove temporary file: %s",
                        temporary_path,
                    )

            return False

    def process_and_store(self, raw_json: List[Dict]) -> bool:
        """Validate data, save it to SQLite, and create a CSV backup."""

        clean_df = self.process_data(raw_json)

        if clean_df is None or clean_df.empty:
            logger.error("Pipeline stopped: no valid data to store.")
            return False

        try:
            database_saved = self.db.save_dataframe(clean_df)

            if not database_saved:
                logger.error("Database storage failed. CSV backup skipped.")
                return False

        except Exception:
            logger.exception("Unexpected database storage error.")
            return False

        if not self.save_csv_backup(clean_df):
            logger.error(
                "Database was updated, but CSV backup could not be saved."
            )
            return False

        logger.info("Market data pipeline completed successfully.")
        return True

    def run(self) -> bool:
        """Execute the complete extraction and storage workflow."""

        raw_json = self.fetch_api_data()

        if raw_json is None:
            logger.error("Pipeline stopped because API extraction failed.")
            return False

        return self.process_and_store(raw_json)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    pipeline = CoinGeckoPipeline()

    try:
        success = pipeline.run()
        if not success:
            raise SystemExit("Crypto Market Pipeline failed.")
    finally:
        pipeline.close()
