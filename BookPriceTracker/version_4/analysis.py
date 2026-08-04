import logging
import pandas as pd
from typing import Dict, Any, Optional
from database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

class CatalogAnalyzer:
    """
    Analytical engine that interfaces directly with the SQL database
    to extract business intelligence, correlation matrices, and metrics.
    """

    def __init__(self, db_path: str = "data/ecommerce_catalog.db"):
        self.db = DatabaseManager(db_path=db_path)

    def load_catalog_data(self) -> pd.DataFrame:
        """Fetches the dataset from SQL database into Pandas."""
        query = "SELECT title, price_gbp, rating, in_stock FROM books;"
        df = self.db.execute_query(query)
        if df is None or df.empty:
            logging.error("Failed to retrieve analytical data from SQL database.")
            return pd.DataFrame()
        return df

    def compute_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates foundational metrics across catalog prices and ratings."""
        if df.empty:
            return {}

        metrics = {
            "total_records": int(len(df)),
            "mean_price": float(df['price_gbp'].mean()),
            "median_price": float(df['price_gbp'].median()),
            "std_dev_price": float(df['price_gbp'].std()),
            "min_price": float(df['price_gbp'].min()),
            "max_price": float(df['price_gbp'].max()),
            "in_stock_rate_pct": float((df['in_stock'].sum() / len(df)) * 100)
        }
        return metrics

    def analyze_price_by_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """Groups data by rating tier to evaluate price distribution across quality scores."""
        if df.empty:
            return pd.DataFrame()

        grouped = (
            df.groupby('rating')['price_gbp']
            .agg(
                item_count='count',
                average_price='mean',
                min_price='min',
                max_price='max'
            )
            .round(2)
            .reset_index()
        )
        return grouped

    def compute_correlation(self, df: pd.DataFrame) -> float:
        """Computes Pearson's Correlation Coefficient between price and rating."""
        if df.empty or len(df) < 2:
            return 0.0
        return float(df['price_gbp'].corr(df['rating']))

    def generate_executive_report(self) -> None:
        """Generates a text report summarizing the pipeline analysis."""
        df = self.load_catalog_data()
        if df.empty:
            logging.error("Aborting report generation: Catalog table is empty.")
            return

        metrics = self.compute_summary_statistics(df)
        grouped_ratings = self.analyze_price_by_rating(df)
        correlation = self.compute_correlation(df)

        report = f"""
======================================================================
               E-COMMERCE PRICE INTELLIGENCE REPORT                  
======================================================================

1. EXECUTIVE SUMMARY
----------------------------------------------------------------------
Total Items Analyzed:      {metrics.get('total_records', 0)}
Catalog Average Price:     £{metrics.get('mean_price', 0.0):.2f}
Price Standard Deviation:  £{metrics.get('std_dev_price', 0.0):.2f}
In-Stock Availability:     {metrics.get('in_stock_rate_pct', 0.0):.1f}%

2. CORRELATION ANALYSIS
----------------------------------------------------------------------
Pearson Correlation (Price vs. Rating): {correlation:.4f}
Interpretation: """

        if abs(correlation) < 0.1:
            report += "No meaningful linear relationship detected between product price and customer rating.\n"
        elif correlation > 0:
            report += "Positive relationship: Higher priced items tend to carry higher ratings.\n"
        else:
            report += "Negative relationship: Higher priced items tend to carry lower ratings.\n"

        report += f"""
3. PRICING BY STAR RATING TIER
----------------------------------------------------------------------
{grouped_ratings.to_string(index=False)}
======================================================================
"""
        print(report)
        logging.info("Executive analytical report generated successfully.")


if __name__ == "__main__":
    analyzer = CatalogAnalyzer()
    analyzer.generate_executive_report()