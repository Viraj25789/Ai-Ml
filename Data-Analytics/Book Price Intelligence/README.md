# Book Price Intelligence

A versioned Python project that demonstrates how to collect, clean, validate, store and analyze e-commerce book catalog data.

## Recommended version

<badge>Latest: Version 4</badge>

Start with [version_4](version_4/). It is the most complete implementation and includes:

- Multi-page scraping with request handling.
- Data cleaning and validation for prices, ratings and stock.
- CSV exports and SQLite persistence.
- Catalog analysis and business summaries.
- Automated tests and a GitHub Actions workflow.

**Setup and run:** Follow the [Version 4 README](version_4/README.md).

## Version history

| Version | Focus | Status |
|---|---|---|
| [Version 1](version_1/) | Initial scraping implementation and basic practice script | Legacy learning version |
| [Version 2](version_2/) | Intermediate scraper iteration | Legacy learning version |
| [Version 3](version_3/) | Modular extraction, cleaning and analysis scripts | Previous iteration |
| [Version 4](version_4/) | Validated ETL pipeline, SQLite storage, analysis and automated tests | Recommended |

Older versions are kept to show how the project evolved. They are not separate projects and are not the recommended starting point.

## Data source

[Books to Scrape](https://books.toscrape.com/) is a demonstration bookstore website intended for practicing web scraping.

## Main technologies

Python, Requests, BeautifulSoup, Pandas, SQLite and pytest.

## Repository layout

```text
Book Price Intelligence/
├── README.md
├── version_1/
├── version_2/
├── version_3/
└── version_4/
```

## Author

[Viraj Parmar](https://github.com/Viraj25789)
