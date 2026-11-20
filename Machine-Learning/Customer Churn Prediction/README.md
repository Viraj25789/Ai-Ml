# Customer Churn Prediction

A supervised machine-learning project that predicts whether a customer is likely to churn using customer demographics, subscription details, service usage, and payment behaviour.

## Business problem

Customer churn affects recurring revenue. A churn prediction model can help a business identify customers who may need attention. This project compares three classification approaches and evaluates how well they generalize to a separate test dataset.

## Dataset

The project uses the provided training and testing CSV files in `data/`.

Example input features:

- Age, gender, and tenure
- Usage frequency and support calls
- Payment delay and total spend
- Subscription type and contract length
- Last interaction

`CustomerID` is an identifier and is excluded from model training.

## Workflow

1. Inspect data quality, missing values, duplicates, and target distribution.
2. Explore churn patterns across subscription type, contract length, and payment delay.
3. Split training data using a stratified 80/20 split.
4. Impute missing values, scale numeric features, and one-hot encode categorical features inside Scikit-learn pipelines.
5. Train Logistic Regression, Decision Tree, and Random Forest models.
6. Compare accuracy, precision, recall, and F1 score on the untouched holdout set.
7. Evaluate the trained models separately on the supplied test CSV to examine generalization.
8. Save the best holdout-F1 pipeline, including preprocessing, to `models/best_churn_model.pkl`.

Class weights are used to address class imbalance without changing the holdout test distribution.

## Repository structure

```text
Customer Churn Prediction/
├── data/
│   ├── dataset-training.csv
│   └── dataset-testing.csv
├── notebooks/
│   └── churn_analysis.ipynb
├── models/                 # generated when the notebook is run
├── requirements.txt
└── README.md
```

## Run locally

Run from this project directory:

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\\Scripts\\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and launch Jupyter:

```bash
pip install -r requirements.txt
jupyter notebook
```

Open `notebooks/churn_analysis.ipynb` and run all cells from top to bottom.

## Evaluation notes

Accuracy is reported alongside precision, recall, and F1 score. Recall is particularly relevant when missing a customer who will churn is costly. The separate test CSV is treated as a generalization check, not as a dataset for tuning model settings.

A performance gap between the internal holdout and separate test data may indicate distribution shift, data quality differences, or overfitting. Near-perfect scores should be investigated rather than accepted at face value.

## Tech stack

Python • Pandas • NumPy • Matplotlib • Scikit-learn • Joblib • Jupyter Notebook
