import pandas as pd

from model.apriori_model import AprioriModel
from model.collaborative_filtering import CollaborativeFiltering


def create_dataset(path):
    # Strong positive association: Laptop and Mouse co-occur in four baskets,
    # while each also appears once alone. Keyboard provides a third item.
    rows = [
        {"TransactionID": i, "UserID": i, "Items": "Laptop, Mouse"}
        for i in range(1, 5)
    ]
    rows.extend([
        {"TransactionID": 5, "UserID": 5, "Items": "Laptop"},
        {"TransactionID": 6, "UserID": 6, "Items": "Mouse"},
    ])
    rows.extend([
        {"TransactionID": i, "UserID": i, "Items": "Keyboard"}
        for i in range(7, 11)
    ])
    pd.DataFrame(rows).to_csv(path, index=False)
    return path

def test_apriori_loads_products_and_generates_rules(tmp_path):
    path = create_dataset(tmp_path / "transactions.csv")

    model = AprioriModel(path)

    assert model.all_items == {"Laptop", "Mouse", "Keyboard"}
    assert not model.rules.empty


def test_apriori_excludes_rules_with_lift_at_or_below_one(tmp_path):
    path = tmp_path / "negative_association.csv"
    pd.DataFrame(
        [
            *[{"TransactionID": i, "UserID": i, "Items": "A, B"} for i in range(1, 4)],
            *[{"TransactionID": i, "UserID": i, "Items": "A"} for i in range(4, 9)],
            *[{"TransactionID": i, "UserID": i, "Items": "B"} for i in range(9, 11)],
        ]
    ).to_csv(path, index=False)

    model = AprioriModel(path)

    # A appears in 8/10 baskets and B in 5/10; their 3 co-occurrences
    # produce lift 0.75, so the pair must not become a recommendation.
    assert model.rules.empty


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
