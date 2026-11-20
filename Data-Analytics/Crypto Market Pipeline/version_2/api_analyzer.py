
import logging
from typing import Any, Dict, Optional

import pandas as pd

from database import CryptoDatabase


logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analyze the latest cryptocurrency market snapshot."""

    LATEST_MARKET_QUERY = """
        SELECT
            asset_name,
            symbol,
            current_price,
            price_change_24h,
            extracted_at
        FROM market_data
        WHERE extracted_at = (
            SELECT MAX(extracted_at)
            FROM market_data
        )
        ORDER BY price_change_24h DESC
    """

    def __init__(self, db: Optional[CryptoDatabase] = None):
        self.db = db or CryptoDatabase()

    def generate_report(self) -> Optional[Dict[str, Any]]:
        """Build a summary from the latest stored market snapshot."""

        df = self.db.execute_query(self.LATEST_MARKET_QUERY)

        if df is None or df.empty:
            logger.warning(
                "No market data found. Run api_pipeline.py first."
            )
            return None

        required_columns = {
            "asset_name",
            "symbol",
            "current_price",
            "price_change_24h",
        }

        missing = required_columns.difference(df.columns)
        if missing:
            logger.error(
                "Market query is missing columns: %s",
                sorted(missing),
            )
            return None

        df = df.copy()
        df["current_price"] = pd.to_numeric(
            df["current_price"], errors="coerce"
        )
        df["price_change_24h"] = pd.to_numeric(
            df["price_change_24h"], errors="coerce"
        )

        df = df.dropna(
            subset=["asset_name", "current_price", "price_change_24h"]
        )

        if df.empty:
            logger.warning("No valid market records available for analysis.")
            return None

        top_gainer = df.loc[df["price_change_24h"].idxmax()]
        top_loser = df.loc[df["price_change_24h"].idxmin()]
        average_change = float(df["price_change_24h"].mean())

        if average_change > 0:
            sentiment = "Bullish"
        elif average_change < 0:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        return {
            "total_assets": int(len(df)),
            "top_gainer": {
                "name": str(top_gainer["asset_name"]),
                "symbol": str(top_gainer["symbol"]),
                "price": float(top_gainer["current_price"]),
                "change": float(top_gainer["price_change_24h"]),
            },
            "top_loser": {
                "name": str(top_loser["asset_name"]),
                "symbol": str(top_loser["symbol"]),
                "price": float(top_loser["current_price"]),
                "change": float(top_loser["price_change_24h"]),
            },
            "average_change": average_change,
            "sentiment": sentiment,
            "data_timestamp": (
                str(df["extracted_at"].iloc[0])
                if "extracted_at" in df.columns
                else "Unavailable"
            ),
        }

    def run_live_report(self) -> bool:
        """Generate and display the latest market report."""

        report = self.generate_report()

        if report is None:
            print("\nNo market report available.")
            print("Run python api_pipeline.py to collect market data.\n")
            return False

        gainer = report["top_gainer"]
        loser = report["top_loser"]

        print("\n" + "=" * 48)
        print("          CRYPTO MARKET REPORT")
        print("=" * 48)

        print(f"Assets analyzed : {report['total_assets']}")
        print(
            f"Top gainer      : {gainer['name']} ({gainer['symbol'].upper()})"
        )
        print(f"Price           : ${gainer['price']:,.4f}")
        print(f"24h change      : {gainer['change']:+.2f}%")

        print("-" * 48)

        print(
            f"Top loser       : {loser['name']} ({loser['symbol'].upper()})"
        )
        print(f"Price           : ${loser['price']:,.4f}")
        print(f"24h change      : {loser['change']:+.2f}%")

        print("-" * 48)

        print(f"Average change  : {report['average_change']:+.2f}%")
        print(f"Market sentiment: {report['sentiment']}")
        print(f"Snapshot time   : {report['data_timestamp']}")

        print("=" * 48 + "\n")

        return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    analyzer = MarketAnalyzer()
    analyzer.run_live_report()
