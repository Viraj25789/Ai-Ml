import pandas as pd
import pytest

from api_analyzer import MarketAnalyzer
from api_pipeline import CoinGeckoPipeline
from database import CryptoDatabase


@pytest.fixture
def sample_records():
    return [
        {
            "name": "Bitcoin",
            "symbol": "btc",
            "current_price": 65000,
            "market_cap": 1200000000,
            "price_change_percentage_24h": 3.5,
            "roi": {"percentage": 12.0},
        },
        {
            "name": "Ethereum",
            "symbol": "eth",
            "current_price": 3200,
            "market_cap": 400000000,
            "price_change_percentage_24h": -1.5,
            "roi": None,
        },
    ]


@pytest.fixture
def pipeline(tmp_path):
    database = CryptoDatabase(str(tmp_path / "market.db"))
    instance = CoinGeckoPipeline(
        db=database,
        output_path=str(tmp_path / "data" / "market.csv"),
    )
    yield instance
    instance.close()


def test_process_data_flattens_and_selects_fields(pipeline, sample_records):
    result = pipeline.process_data(sample_records)

    assert result is not None
    assert len(result) == 2
    assert "roi.percentage" in result.columns
    assert result.iloc[0]["name"] == "Bitcoin"


def test_process_data_rejects_missing_required_fields(pipeline):
    result = pipeline.process_data([{"name": "Bitcoin", "symbol": "btc"}])

    assert result is None


def test_process_data_rejects_empty_input(pipeline):
    assert pipeline.process_data([]) is None


def test_process_data_skips_invalid_market_records(pipeline):
    records = [
        {
            "name": "Invalid",
            "symbol": "bad",
            "current_price": "not-a-price",
            "market_cap": 100,
            "price_change_percentage_24h": 1,
        },
        {
            "name": "Valid",
            "symbol": "ok",
            "current_price": 10,
            "market_cap": 100,
            "price_change_percentage_24h": 1,
        },
    ]

    result = pipeline.process_data(records)

    assert result is not None
    assert len(result) == 1
    assert result.iloc[0]["name"] == "Valid"


def test_save_csv_backup_creates_file(pipeline, sample_records):
    df = pipeline.process_data(sample_records)

    assert pipeline.save_csv_backup(df) is True
    saved = pd.read_csv(pipeline.output_path)
    assert len(saved) == 2


def test_empty_csv_backup_is_rejected(pipeline):
    assert pipeline.save_csv_backup(pd.DataFrame()) is False
    assert not pipeline.output_path.exists()


def test_process_and_store_saves_database_and_csv(pipeline, sample_records):
    assert pipeline.process_and_store(sample_records) is True

    saved = pipeline.db.execute_query("SELECT * FROM market_data")
    assert saved is not None
    assert len(saved) == 2
    assert pipeline.output_path.exists()


def test_process_and_store_rejects_invalid_payload(pipeline):
    assert pipeline.process_and_store([{"bad": "data"}]) is False
    saved = pipeline.db.execute_query("SELECT * FROM market_data")
    assert saved.empty


def test_fetch_api_data_returns_valid_list(pipeline, sample_records, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return sample_records

    monkeypatch.setattr(
        pipeline.session,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )

    assert pipeline.fetch_api_data() == sample_records


def test_fetch_api_data_rejects_non_list_response(pipeline, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"error": "invalid response"}

    monkeypatch.setattr(
        pipeline.session,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )

    assert pipeline.fetch_api_data() is None


def test_analyzer_identifies_gainer_loser_and_sentiment(pipeline, sample_records):
    assert pipeline.process_and_store(sample_records) is True

    analyzer = MarketAnalyzer(db=pipeline.db)
    report = analyzer.generate_report()

    assert report is not None
    assert report["top_gainer"]["name"] == "Bitcoin"
    assert report["top_loser"]["name"] == "Ethereum"
    assert report["sentiment"] == "Bullish"
    assert report["total_assets"] == 2


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ([2.0, 1.0], "Bullish"),
        ([-2.0, -1.0], "Bearish"),
        ([1.0, -1.0], "Neutral"),
    ],
)
def test_analyzer_market_sentiment(pipeline, changes, expected):
    records = []
    for index, change in enumerate(changes):
        records.append(
            {
                "name": f"Coin {index}",
                "symbol": f"coin{index}",
                "current_price": 10 + index,
                "market_cap": 1000,
                "price_change_percentage_24h": change,
            }
        )

    assert pipeline.process_and_store(records) is True

    report = MarketAnalyzer(db=pipeline.db).generate_report()

    assert report["sentiment"] == expected


def test_analyzer_returns_none_when_database_is_empty(pipeline):
    analyzer = MarketAnalyzer(db=pipeline.db)

    assert analyzer.generate_report() is None



def test_analyzer_uses_only_the_latest_snapshot(pipeline, sample_records):
    first_batch = sample_records
    second_batch = [
        {
            "name": "Solana",
            "symbol": "sol",
            "current_price": 150,
            "market_cap": 70000000,
            "price_change_percentage_24h": 8.0,
        }
    ]

    assert pipeline.process_and_store(first_batch) is True
    assert pipeline.process_and_store(second_batch) is True

    report = MarketAnalyzer(db=pipeline.db).generate_report()

    assert report is not None
    assert report["total_assets"] == 1
    assert report["top_gainer"]["name"] == "Solana"
