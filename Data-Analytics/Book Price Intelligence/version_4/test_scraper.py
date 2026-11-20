
import pandas as pd
import pytest
from bs4 import BeautifulSoup

from scraper import ECommerceScraper


@pytest.fixture
def scraper(tmp_path):
    return ECommerceScraper(
        base_url="https://example.com/page-{}.html",
        output_path=str(tmp_path / "data" / "raw_books.csv"),
        request_delay=0,
    )


@pytest.fixture
def valid_html():
    return """
    <article class="product_pod">
        <h3><a title="Test Book">Test Book</a></h3>
        <p class="price_color">£25.99</p>
        <p class="instock availability">In stock</p>
        <p class="star-rating Three"></p>
    </article>
    """


def test_extract_valid_book(scraper, valid_html):
    soup = BeautifulSoup(valid_html, "html.parser")

    books = scraper.extract_books(soup)

    assert len(books) == 1
    assert books[0]["Title"] == "Test Book"
    assert books[0]["Price"] == "£25.99"
    assert books[0]["Rating"] == "Three"


def test_extract_skips_incomplete_book(scraper):
    html = """
    <article class="product_pod">
        <h3><a title="Incomplete Book">Book</a></h3>
    </article>
    """

    books = scraper.extract_books(
        BeautifulSoup(html, "html.parser")
    )

    assert books == []


def test_save_data_creates_csv(scraper):
    books = [{
        "Title": "Test Book",
        "Price": "£25.99",
        "Stock_Status": "In stock",
        "Rating": "Three",
    }]

    assert scraper._save_data(books) is True

    result = pd.read_csv(scraper.output_path)

    assert len(result) == 1
    assert result.iloc[0]["Title"] == "Test Book"


def test_empty_data_does_not_create_csv(scraper):
    assert scraper._save_data([]) is False
    assert not pd.io.common.file_exists(scraper.output_path)


def test_failed_page_does_not_overwrite_existing_data(
    scraper, monkeypatch
):
    existing_data = "Title,Price,Stock_Status,Rating\nOld Book,£10,In stock,Five\n"

    import os
    os.makedirs(os.path.dirname(scraper.output_path), exist_ok=True)

    with open(scraper.output_path, "w", encoding="utf-8") as file:
        file.write(existing_data)

    monkeypatch.setattr(
        scraper,
        "fetch_page",
        lambda page_num: None,
    )

    assert scraper.run(num_pages=2) is False

    with open(scraper.output_path, encoding="utf-8") as file:
        assert file.read() == existing_data


def test_invalid_page_count_raises_error(scraper):
    with pytest.raises(ValueError):
        scraper.run(num_pages=0)

    with pytest.raises(ValueError):
        scraper.run(num_pages=-1)
