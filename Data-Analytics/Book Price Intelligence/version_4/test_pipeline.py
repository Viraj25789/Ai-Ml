import pytest
import pandas as pd
from bs4 import BeautifulSoup
from cleaner import DataCleaner

@pytest.fixture
def sample_raw_dataframe():
    """Provides a synthetic uncleaned raw dataset for transformer testing."""
    return pd.DataFrame({
        'Title': ['Test Book A', 'Test Book B', 'Test Book C'],
        'Price': ['£51.77', '£10.25', '£0.00'],
        'Stock_Status': ['In stock (22 available)', 'In stock', 'Out of stock'],
        'Rating': ['Three', 'Five', 'One']
    })

@pytest.fixture
def sample_html_element():
    """Provides mock HTML representing a single product element on the target site."""
    html = """
    <article class="product_pod">
        <h3><a title="A Light in the Attic">A Light in the ...</a></h3>
        <p class="price_color">£51.77</p>
        <p class="instock availability"><i class="icon-ok"></i>In stock</p>
        <p class="star-rating Three"></p>
    </article>
    """
    return BeautifulSoup(html, 'html.parser')

def test_data_cleaner_transform(sample_raw_dataframe):
    """Tests if price stripping, rating mapping, and stock conversion perform accurately."""
    cleaner = DataCleaner()
    cleaned_df = cleaner.transform(sample_raw_dataframe)

    # Assert Price Conversion
    assert cleaned_df['Price'].dtype == float
    assert cleaned_df['Price'].iloc[0] == 51.77
    assert cleaned_df['Price'].iloc[1] == 10.25

    # Assert Rating Conversion
    assert cleaned_df['Rating'].dtype == int
    assert cleaned_df['Rating'].iloc[0] == 3
    assert cleaned_df['Rating'].iloc[1] == 5
    assert cleaned_df['Rating'].iloc[2] == 1

    # Assert Stock Boolean Conversion
    assert cleaned_df['In_Stock'].dtype == bool
    assert cleaned_df['In_Stock'].iloc[0] is True
    assert cleaned_df['In_Stock'].iloc[2] is False

def test_rating_map_completeness():
    """Validates that all target rating string values map correctly."""
    cleaner = DataCleaner()
    assert len(cleaner.RATING_MAP) == 5
    assert cleaner.RATING_MAP['Five'] == 5