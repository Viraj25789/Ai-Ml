
import logging
from typing import Any, Dict

import pandas as pd

from database import DatabaseManager

logger = logging.getLogger(__name__)


class CatalogAnalyzer:
    """Analyze book catalog data and generate business insights."""

    def __init__(self, db_path: str = "data/ecommerce_catalog.db"):
        self.db = DatabaseManager(db_path=db_path)

    def load_catalog_data(self) -> pd.DataFrame:
        """Load catalog records from SQLite."""
        query = """
            SELECT title, price_gbp, rating, in_stock
            FROM books
        """

        df = self.db.execute_query(query)

        if df is None or df.empty:
            logger.warning("No catalog records available for analysis.")
            return pd.DataFrame()

        return df

    def compute_summary_statistics(
        self,
        df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Calculate key descriptive statistics."""
        if df.empty:
            return {}

        prices = pd.to_numeric(df["price_gbp"], errors="coerce").dropna()

        if prices.empty:
            return {}

        stock_count = int(df["in_stock"].astype(bool).sum())
        total_records = len(df)

        standard_deviation = prices.std()
        if pd.isna(standard_deviation):
            standard_deviation = 0.0

        return {
            "total_records": total_records,
            "mean_price": float(prices.mean()),
            "median_price": float(prices.median()),
            "std_dev_price": float(standard_deviation),
            "min_price": float(prices.min()),
            "max_price": float(prices.max()),
            "in_stock_count": stock_count,
            "out_of_stock_count": total_records - stock_count,
            "in_stock_rate_pct": float(
                stock_count / total_records * 100
            ),
        }

    def analyze_price_by_rating(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Compare price distribution across rating groups."""
        if df.empty:
            return pd.DataFrame()

        return (
            df.groupby("rating")["price_gbp"]
            .agg(
                item_count="count",
                average_price="mean",
                min_price="min",
                max_price="max",
            )
            .round(2)
            .reset_index()
            .sort_values("rating")
        )

    def compute_correlation(self, df: pd.DataFrame):
        """Calculate price-rating correlation when meaningful."""
        if df.empty or len(df) < 2:
            return None

        if (
            df["price_gbp"].nunique() < 2
            or df["rating"].nunique() < 2
        ):
            return None

        correlation = df["price_gbp"].corr(df["rating"])

        if pd.isna(correlation):
            return None

        return float(correlation)

    def find_price_extremes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify the cheapest and most expensive books."""
        if df.empty:
            return {}

        cheapest = df.loc[df["price_gbp"].idxmin()]
        expensive = df.loc[df["price_gbp"].idxmax()]

        return {
            "cheapest_title": cheapest["title"],
            "cheapest_price": float(cheapest["price_gbp"]),
            "most_expensive_title": expensive["title"],
            "most_expensive_price": float(expensive["price_gbp"]),
        }

    def generate_executive_report(self) -> str:
        """Generate and print a concise catalog intelligence report."""
        df = self.load_catalog_data()

        if df.empty:
            logger.error("Report generation stopped: no catalog data.")
            return ""

        metrics = self.compute_summary_statistics(df)

        if not metrics:
            logger.error("Report generation stopped: no valid prices.")
            return ""

        grouped_ratings = self.analyze_price_by_rating(df)
        correlation = self.compute_correlation(df)
        extremes = self.find_price_extremes(df)

        if correlation is None:
            correlation_text = (
                "Not available (insufficient variation or data)."
            )
        elif abs(correlation) < 0.1:
            correlation_text = (
                f"{correlation:.4f} - Very weak linear relationship."
            )
        elif correlation > 0:
            correlation_text = (
                f"{correlation:.4f} - Positive linear relationship."
            )
        else:
            correlation_text = (
                f"{correlation:.4f} - Negative linear relationship."
            )

        report = f"""
================================================================
              BOOK PRICE INTELLIGENCE REPORT
================================================================

1. CATALOG OVERVIEW
----------------------------------------------------------------
Total Books Analyzed:       {metrics['total_records']}
Average Book Price:         £{metrics['mean_price']:.2f}
Median Book Price:          £{metrics['median_price']:.2f}
Price Standard Deviation:   £{metrics['std_dev_price']:.2f}
Minimum Book Price:         £{metrics['min_price']:.2f}
Maximum Book Price:         £{metrics['max_price']:.2f}

2. INVENTORY ANALYSIS
----------------------------------------------------------------
Books In Stock:             {metrics['in_stock_count']}
Books Out of Stock:         {metrics['out_of_stock_count']}
Availability Rate:          {metrics['in_stock_rate_pct']:.1f}%

3. PRICE EXTREMES
----------------------------------------------------------------
Cheapest Book:
  {extremes['cheapest_title']}
  Price: £{extremes['cheapest_price']:.2f}

Most Expensive Book:
  {extremes['most_expensive_title']}
  Price: £{extremes['most_expensive_price']:.2f}

4. PRICE VS RATING ANALYSIS
----------------------------------------------------------------
Pearson Correlation: {correlation_text}

Note: Correlation describes a linear association. It does not
establish that price causes a higher or lower customer rating.

5. AVERAGE PRICE BY RATING
----------------------------------------------------------------
{grouped_ratings.to_string(index=False)}

================================================================
"""

        print(report)
        logger.info("Catalog intelligence report generated.")

        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = CatalogAnalyzer()
    analyzer.generate_executive_report()
