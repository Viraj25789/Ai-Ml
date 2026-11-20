import pandas as pd

from model.apriori_model import AprioriModel
from model.collaborative_filtering import CollaborativeFiltering


def create_dataset(path):
    df = pd.DataFrame(
        [
            {"TransactionID": 1, "UserID": 101, "Items": "Laptop, Mouse"},
            {"TransactionID": 2, "UserID": 101, "Items": "Laptop, Keyboard"},
            {"TransactionID": 3, "UserID": 102, "Items": "Laptop, Mouse"},
            {"TransactionID": 4, "UserID": 102, "Items": "Laptop, Keyboard"},
            {"TransactionID": 5, "UserID": 103, "Items": "Mouse, Keyboard"},
            {"TransactionID": 6, "UserID": 103, "Items": "Mouse, Laptop"},
        ]
    )
    df.to_csv(path, index=False)
    return path


def test_apriori_loads_products_and_generates_rules(tmp_path):
    path = create_dataset(tmp_path / "transactions.csv")

    model = AprioriModel(path)

    assert model.all_items == {"Laptop", "Mouse", "Keyboard"}
    assert not model.rules.empty


def test_apriori_returns_product_associations(tmp_path):
    path = create_dataset(tmp_path / "transactions.csv")

    model = AprioriModel(path)

    assert "Laptop" in model.recommend("Mouse")


def test_apriori_chart_data_has_matching_lengths(tmp_path):
    path = create_dataset(tmp_path / "transactions.csv")

    chart = AprioriModel(path).get_top_rules_chart_data()

    assert len(chart["labels"]) == len(chart["confidence"])
    assert len(chart["labels"]) == len(chart["lift"])


def test_markov_prediction_excludes_already_purchased_items(tmp_path):
    path = create_dataset(tmp_path / "transactions.csv")

    predictions = AprioriModel(path).predict_next(["Laptop"], top_n=5)

    assert predictions
    assert all(row["item"] != "Laptop" for row in predictions)
    assert all(0 <= row["pct"] <= 100 for row in predictions)


def test_collaborative_filtering_builds_user_item_matrix(tmp_path):
    path = create_dataset(tmp_path / "transactions.csv")

    model = CollaborativeFiltering(path)

    assert model.user_item_matrix is not None
    assert len(model.user_item_matrix.index) == 3
    assert set(model.all_items) == {"Laptop", "Mouse", "Keyboard"}
    assert model.get_popular_items(top_n=2)


def test_markov_does_not_invent_order_inside_a_basket(tmp_path):
    path = tmp_path / "unordered.csv"
    pd.DataFrame([
        {"TransactionID": 1, "UserID": 1, "Items": "Bread, Milk"},
    ]).to_csv(path, index=False)

    model = AprioriModel(path)

    assert not model._transitions


def test_markov_learns_transitions_between_user_baskets(tmp_path):
    path = tmp_path / "sequence.csv"
    pd.DataFrame([
        {"TransactionID": 1, "UserID": 1, "Items": "Bread, Milk"},
        {"TransactionID": 2, "UserID": 1, "Items": "Eggs"},
        {"TransactionID": 3, "UserID": 2, "Items": "Coffee"},
    ]).to_csv(path, index=False)

    model = AprioriModel(path)

    assert model._transitions["Bread"]["Eggs"] == 1
    assert model._transitions["Milk"]["Eggs"] == 1
    assert "Milk" not in model._transitions["Bread"]
