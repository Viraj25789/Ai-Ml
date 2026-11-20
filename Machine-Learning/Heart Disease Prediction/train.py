"""Train a reproducible, leakage-safe heart-disease classification baseline.

Educational project only. This model is not a medical diagnostic tool.
"""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "heart.csv"
MODEL_PATH = ROOT / "models" / "heart_disease_pipeline.joblib"
NUMERIC = ["Age", "RestingBP", "Cholesterol", "FastingBS", "MaxHR", "Oldpeak"]
CATEGORICAL = ["Sex", "ChestPainType", "RestingECG", "ExerciseAngina", "ST_Slope"]
TARGET = "HeartDisease"


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    required = NUMERIC + CATEGORICAL + [TARGET]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = df[required].copy()
    for col in NUMERIC + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # In this dataset, zero blood pressure/cholesterol values represent missing measurements.
    for col in ["RestingBP", "Cholesterol"]:
        df.loc[df[col] == 0, col] = float("nan")
    df = df.dropna(subset=[TARGET])
    df = df[df[TARGET].isin([0, 1])]
    if df.empty:
        raise ValueError("No valid labeled rows in dataset.")
    class_counts = df[TARGET].value_counts()
    if len(class_counts) != 2:
        raise ValueError("HeartDisease must contain both classes 0 and 1.")
    if class_counts.min() < 2:
        raise ValueError(
            "Each HeartDisease class needs at least two rows for a stratified split."
        )
    return df


def build_pipeline():
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    prep = ColumnTransformer([
        ("numeric", numeric, NUMERIC),
        ("categorical", categorical, CATEGORICAL),
    ])
    return Pipeline([
        ("preprocessing", prep),
        ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])


def train(data_path=DATA_PATH, model_path=MODEL_PATH):
    df = load_data(data_path)
    X, y = df[NUMERIC + CATEGORICAL], df[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = build_pipeline()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    probability = model.predict_proba(X_test)[:, 1]
    print(f"Rows: {len(df)} | Train: {len(X_train)} | Holdout: {len(X_test)}")
    print(f"Accuracy: {accuracy_score(y_test, pred):.3f}")
    print(f"F1: {f1_score(y_test, pred):.3f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probability):.3f}")
    print(classification_report(y_test, pred, zero_division=0))
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Saved pipeline: {model_path}")
    return model


if __name__ == "__main__":
    train()
