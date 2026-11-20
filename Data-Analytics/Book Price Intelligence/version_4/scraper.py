
import logging
import os
import time
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ECommerceScraper:
    """Scrape book catalog data with retries and safe CSV export."""

    REQUIRED_FIELDS = ["Title", "Price", "Stock_Status", "Rating"]

    def __init__(
        self,
        base_url: str,
        output_path: str = "data/raw_books.csv",
        request_delay: float = 1.0,
    ):
        self.base_url = base_url
        self.output_path = output_path
        self.request_delay = max(0.0, request_delay)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            )
        })

        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_page(self, page_num: int) -> Optional[BeautifulSoup]:
        """Fetch one catalog page, returning None if the request fails."""
        url = self.base_url.format(page_num)

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")

        except requests.RequestException as error:
            logger.error("Failed to fetch page %s: %s", page_num, error)
            return None

    def extract_books(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract valid book fields from a catalog page."""
        page_data = []

        for book in soup.find_all("article", class_="product_pod"):
            try:
                title_element = book.select_one("h3 a")
                price_element = book.select_one("p.price_color")
                stock_element = book.select_one("p.instock.availability")
                rating_element = book.select_one("p.star-rating")

                if not all([
                    title_element,
                    price_element,
                    stock_element,
                    rating_element,
                ]):
                    logger.warning("Skipping incomplete book listing.")
                    continue

                rating_classes = rating_element.get("class", [])
                rating = next(
                    (value for value in rating_classes if value in {
                        "One", "Two", "Three", "Four", "Five"
                    }),
                    None,
                )

                title = title_element.get("title", "").strip()
                price = price_element.get_text(strip=True)
                stock = stock_element.get_text(" ", strip=True)

                if not title or not price or not rating:
                    logger.warning("Skipping book with invalid fields.")
                    continue

                page_data.append({
                    "Title": title,
                    "Price": price,
                    "Stock_Status": stock,
                    "Rating": rating,
                })

            except (AttributeError, TypeError, KeyError) as error:
                logger.warning("Could not parse a book listing: %s", error)

        return page_data

    def _save_data(self, books: List[Dict[str, str]]) -> bool:
        """Write the complete dataset without risking an old valid CSV."""
        if not books:
            logger.error("No book records available to save.")
            return False

        output_directory = os.path.dirname(self.output_path) or "."
        os.makedirs(output_directory, exist_ok=True)

        temporary_path = self.output_path + ".tmp"

        try:
            df = pd.DataFrame(books, columns=self.REQUIRED_FIELDS)
            df.to_csv(temporary_path, index=False)
            os.replace(temporary_path, self.output_path)

            logger.info(
                "Saved %s book records to %s",
                len(df),
                self.output_path,
            )
            return True

        except (OSError, ValueError) as error:
            logger.exception("Could not save scraped data: %s", error)

            if os.path.exists(temporary_path):
                os.remove(temporary_path)

            return False

    def run(self, num_pages: int = 5) -> bool:
        """Scrape all requested pages and save only a complete scrape."""
        if (
            isinstance(num_pages, bool)
            or not isinstance(num_pages, int)
            or num_pages < 1
        ):
            raise ValueError("num_pages must be a positive integer.")

        logger.info("Starting scraper for %s pages.", num_pages)

        all_books = []

        try:
            for page_num in range(1, num_pages + 1):
                soup = self.fetch_page(page_num)

                # Do not overwrite good data with a partial scrape.
                if soup is None:
                    logger.error(
                        "Scrape aborted because page %s failed.",
                        page_num,
                    )
                    return False

                books = self.extract_books(soup)

                if not books:
                    logger.error(
                        "Scrape aborted: no books extracted from page %s.",
                        page_num,
                    )
                    return False

                all_books.extend(books)

                logger.info(
                    "Page %s: extracted %s books.",
                    page_num,
                    len(books),
                )

                if page_num < num_pages and self.request_delay:
                    time.sleep(self.request_delay)

            return self._save_data(all_books)

        finally:
            self.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    target_url = "https://books.toscrape.com/catalogue/page-{}.html"

    scraper = ECommerceScraper(base_url=target_url)
    success = scraper.run(num_pages=5)

    if success:
        logger.info("Scraping completed successfully.")
    else:
        logger.error("Scraping did not complete successfully.")
