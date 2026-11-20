# Ford Car Price Prediction

A regression project that estimates the selling price of used Ford cars from vehicle specifications.

## Business problem

Used-car prices vary with model, age, mileage, transmission, fuel type, tax, fuel economy and engine size. This project explores those relationships and builds a reproducible baseline model to estimate car prices.

## Dataset

The project uses the Ford used-car dataset in `data/ford.csv`.

**Target:** `price`

**Features:** `model`, `year`, `transmission`, `mileage`, `fuelType`, `tax`, `mpg`, and `engineSize`.

## Modeling workflow

The recommended, reproducible training workflow is implemented in `train.py`:

1. Validate required columns and remove rows with missing target prices.
2. Split data into training and holdout sets (80/20, fixed random seed).
3. Impute missing numeric values with the median and scale numeric features.
4. Impute missing categorical values with the most frequent value and one-hot encode categories.
5. Fit preprocessing and Linear Regression together in a Scikit-learn Pipeline. All preprocessing is learned from the training split only.
6. Evaluate on the untouched holdout set using MAE, RMSE, R² and adjusted R².
7. Save the fitted pipeline to `models/ford_price_model.joblib`.

The notebook `main.ipynb` is retained as an exploratory learning artifact. Use `train.py` for the clean training and evaluation workflow.

## Project structure

```text
Car Price Prediction/
├── data/
│   └── ford.csv
├── models/                 # Created when training runs
├── tests/
│   └── test_train.py
├── main.ipynb              # Exploratory analysis
├── train.py                # Reproducible model pipeline
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Train the model

Run from this project directory:

```bash
python train.py
```

The script prints holdout metrics and creates `models/ford_price_model.joblib`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Evaluation metrics

- **MAE:** average absolute prediction error, in the dataset's price units.
- **RMSE:** penalizes larger prediction errors more heavily.
- **R²:** proportion of target variation explained by the model.
- **Adjusted R²:** R² adjusted for the number of input features; omitted when the holdout sample is too small for a valid calculation.

## Limitations

- This is a baseline Linear Regression model, not a production vehicle valuation service.
- The data represents Ford listings and may not generalize to other brands, regions or market periods.
- Prices depend on factors not present in the dataset, such as condition, service history, accident history and location.
- Model performance should be judged from the holdout metrics printed by the training script, not assumed in advance.

## Tech stack

Python, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, Joblib, Jupyter and unittest.
