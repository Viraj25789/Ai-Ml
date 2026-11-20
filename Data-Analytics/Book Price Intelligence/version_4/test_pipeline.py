
import pandas as pd
import pytest

from cleaner import DataCleaner
from database import DatabaseManager


@pytest.fixture
def sample_raw_dataframe():
    return pd.DataFrame({
        "Title": ["Book A", "Book B", "Book C"],
        "Price": ["£51.77", "£10.25", "£0.00"],
        "Stock_Status": [
            "In stock (22 available)",
            "In stock",
            "Out of stock",
        ],
        "Rating": ["Three", "Five", "One"],
    })


@pytest.fixture
def cleaner():
    return DataCleaner()


@pytest.fixture
def database(tmp_path):
    db_path = tmp_path / "test_catalog.db"
    return DatabaseManager(str(db_path))


def test_price_conversion(cleaner, sample_raw_dataframe):
    result = cleaner.transform(sample_raw_dataframe)

    assert result["Price"].tolist() == [51.77, 10.25, 0.00]
    assert pd.api.types.is_numeric_dtype(result["Price"])


def test_rating_conversion(cleaner, sample_raw_dataframe):
    result = cleaner.transform(sample_raw_dataframe)

    assert result["Rating"].tolist() == [3, 5, 1]
    assert result["Rating"].dtype == int


def test_stock_conversion(cleaner, sample_raw_dataframe):
    result = cleaner.transform(sample_raw_dataframe)

    assert result["In_Stock"].tolist() == [True, True, False]
    assert result["In_Stock"].dtype == bool


def test_invalid_records_are_removed(cleaner):
    df = pd.DataFrame({
        "Title": ["Valid", "", "Invalid Price", "Invalid Rating"],
        "Price": ["£20.00", "£10.00", "unknown", "£15.00"],
        "Stock_Status": ["In stock"] * 4,
        "Rating": ["Five", "Four", "Three", "Six"],
    })

    result = cleaner.transform(df)

    assert len(result) == 1
    assert result.iloc[0]["Title"] == "Valid"


def test_numeric_ratings_are_supported(cleaner):
    df = pd.DataFrame({
        "Title": ["Book A", "Book B"],
        "Price": ["£10.00", "£20.00"],
        "Stock_Status": ["In stock", "Out of stock"],
        "Rating": [4, 5],
    })

    result = cleaner.transform(df)

    assert result["Rating"].tolist() == [4, 5]


def test_missing_required_columns_raise_error(cleaner):
    df = pd.DataFrame({
        "Title": ["Book A"],
        "Price": ["£10.00"],
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        cleaner.transform(df)


def test_empty_dataframe(cleaner):
    df = pd.DataFrame(columns=[
        "Title", "Price", "Rating", "Stock_Status"
    ])

    result = cleaner.transform(df)

    assert result.empty
    assert list(result.columns) == [
        "Title", "Price", "Rating", "In_Stock"
    ]


def test_database_insert(database, sample_raw_dataframe):
    cleaner = DataCleaner()
    clean_df = cleaner.transform(sample_raw_dataframe)

    assert database.save_dataframe(clean_df) is True

    result = database.execute_query("SELECT * FROM books")

    assert result is not None
    assert len(result) == 3


def test_database_refresh_prevents_duplicates(database):
    first_df = pd.DataFrame({
        "Title": ["Book A", "Book B"],
        "Price": [10.0, 20.0],
        "Rating": [4, 5],
        "In_Stock": [True, False],
    })

    second_df = pd.DataFrame({
        "Title": ["Book C"],
        "Price": [30.0],
        "Rating": [3],
        "In_Stock": [True],
    })

    assert database.save_dataframe(first_df) is True
    assert database.save_dataframe(second_df) is True

    result = database.execute_query("SELECT title FROM books")

    assert result["title"].tolist() == ["Book C"]
    assert len(result) == 1


def test_empty_database_input_does_not_delete_existing_data(database):
    df = pd.DataFrame({
        "Title": ["Book A"],
        "Price": [10.0],
        "Rating": [4],
        "In_Stock": [True],
    })

    assert database.save_dataframe(df) is True
    assert database.save_dataframe(pd.DataFrame()) is False

    result = database.execute_query("SELECT * FROM books")

    assert len(result) == 1


def test_invalid_database_input_does_not_delete_existing_data(database):
    valid_df = pd.DataFrame({
        "Title": ["Book A"],
        "Price": [10.0],
        "Rating": [4],
        "In_Stock": [True],
    })

    invalid_df = pd.DataFrame({
        "Title": ["Invalid Book"],
        "Price": [-10.0],
        "Rating": [4],
        "In_Stock": [True],
    })

    assert database.save_dataframe(valid_df) is True
    assert database.save_dataframe(invalid_df) is False

    result = database.execute_query("SELECT title FROM books")

    assert result["title"].tolist() == ["Book A"]



def test_unknown_stock_status_is_removed(cleaner):
    df = pd.DataFrame({
        "Title": ["Known", "Unknown"],
        "Price": ["£10.00", "£12.00"],
        "Stock_Status": ["In stock", "status unavailable"],
        "Rating": ["Four", "Five"],
    })

    result = cleaner.transform(df)

    assert result["Title"].tolist() == ["Known"]


@pytest.mark.parametrize(
    ("price", "rating", "stock"),
    [
        (float("inf"), 4, True),
        (10.0, 4.5, True),
        (10.0, 4, "False"),
    ],
)
def test_database_rejects_invalid_values_without_replacing_data(
    database, price, rating, stock
):
    existing = pd.DataFrame({
        "Title": ["Existing Book"],
        "Price": [9.99],
        "Rating": [4],
        "In_Stock": [True],
    })
    invalid = pd.DataFrame({
        "Title": ["Invalid Book"],
        "Price": [price],
        "Rating": [rating],
        "In_Stock": [stock],
    })

    assert database.save_dataframe(existing) is True
    assert database.save_dataframe(invalid) is False

    saved = database.execute_query("SELECT title FROM books")
    assert saved["title"].tolist() == ["Existing Book"]
