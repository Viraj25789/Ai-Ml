# Crypto Market Data Pipeline

A versioned Python project demonstrating how to collect cryptocurrency market data from a public REST API, transform JSON responses, store snapshots and analyze market movements.

## Recommended version

**Latest: Version 2**

Start with [version_2](version_2/). It is the more complete implementation and includes:

- CoinGecko API extraction with request timeouts and retry handling.
- Data validation and transformation with Pandas.
- Historical snapshot storage in SQLite.
- CSV backup with safe file replacement.
- Analysis of the latest stored market snapshot.
- Automated tests and a GitHub Actions workflow.

**Setup and run:** Follow the [Version 2 README](version_2/README.md).

## Version history

| Version | Focus | Status |
|---|---|---|
| [Version 1](version_1/) | Basic API extraction, JSON flattening and market analysis | Legacy learning version |
| [Version 2](version_2/) | Validated API pipeline, SQLite history, robust CSV export and tests | Recommended |

Version 1 is preserved to show the initial implementation. It is not the recommended starting point.

## Data source

[CoinGecko API](https://www.coingecko.com/en/api) provides cryptocurrency market data. API availability and request limits may change.

## Main technologies

Python, Requests, Pandas, REST APIs, JSON, SQLite and pytest.

## Repository layout

```text
Crypto Market Pipeline/
├── README.md
├── version_1/
└── version_2/
```

## Important note

This project is for data engineering and analytics practice. Market summaries are descriptive and are not investment advice.

## Author

[Viraj Parmar](https://github.com/Viraj25789)
