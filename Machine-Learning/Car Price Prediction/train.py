"""Train and evaluate a leakage-safe Ford used-car price model."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "ford.csv"
MODEL_PATH = ROOT / "models" / "ford_price_model.joblib"
TARGET = "price"
NUMERIC_FEATURES = ["year", "mileage", "tax", "mpg", "engineSize"]
CATEGORICAL_FEATURES = ["model", "transmission", "fuelType"]


def load_data(path=DATA_PATH):
    """Load the dataset and validate the columns needed for training."""
    data = pd.read_csv(path)
    required = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    data = data[required].copy()
    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")
    data = data.dropna(subset=[TARGET])
    if data.empty:
        raise ValueError("No rows with a valid target price were found.")
    return data


def build_pipeline():
    """Build preprocessing and regression as one leakage-safe pipeline."""
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessing = ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])
    return Pipeline([
        ("preprocessing", preprocessing),
        ("regressor", LinearRegression()),
    ])


def evaluate(y_true, predictions, feature_count):
    """Return interpretable regression metrics."""
    r2 = r2_score(y_true, predictions)
    n = len(y_true)
    adjusted_r2 = (
        1 - (1 - r2) * (n - 1) / (n - feature_count - 1)
        if n > feature_count + 1 else None
    )
    return {
        "mae": float(mean_absolute_error(y_true, predictions)),
        "rmse": float(mean_squared_error(y_true, predictions) ** 0.5),
        "r2": float(r2),
        "adjusted_r2": float(adjusted_r2) if adjusted_r2 is not None else None,
    }


def train(data_path=DATA_PATH, model_path=MODEL_PATH):
    data = load_data(data_path)
    X = data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = build_pipeline()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    feature_count = len(NUMERIC_FEATURES) + len(CATEGORICAL_FEATURES)
    metrics = evaluate(y_test, predictions, feature_count)

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"Rows: {len(data):,} | Train: {len(X_train):,} | Test: {len(X_test):,}")
    print("Holdout metrics:")
    for name, value in metrics.items():
        print(f"  {name.upper()}: {value:.4f}" if value is not None else f"  {name.upper()}: not available")
    print(f"Saved model: {model_path}")
    return model, metrics


if __name__ == "__main__":
    train()
