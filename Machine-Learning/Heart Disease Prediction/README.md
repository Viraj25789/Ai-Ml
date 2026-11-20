# Heart Disease Classification — Educational ML Project

A supervised machine-learning project using a public heart-disease dataset. It explores clinical-style tabular features and trains a reproducible classification baseline.

> **Safety:** This is an educational portfolio project, not a medical device or clinically validated model. Its predictions must not be used for diagnosis, treatment, screening, or personal health decisions.

## Dataset

Source file: `data/heart.csv`

Target: `HeartDisease` (0 or 1).

Input features include age, sex, chest-pain category, resting blood pressure, cholesterol, fasting blood sugar, resting ECG, maximum heart rate, exercise-induced angina, oldpeak and ST slope.

## Workflow

1. Validate required columns and target labels.
2. Treat zero values in resting blood pressure and cholesterol as missing measurements.
3. Split into stratified training and holdout sets.
4. Impute numeric and categorical missing values.
5. Scale numeric features and one-hot encode categorical features.
6. Fit a class-weighted Logistic Regression baseline.
7. Evaluate on the holdout set using accuracy, F1, ROC-AUC and a classification report.
8. Save the complete preprocessing + model pipeline.

Preprocessing is inside the Scikit-learn pipeline, so imputation, scaling and encoding are learned from the training split only.

## Project structure

```text
Heart Disease Prediction/
├── data/heart.csv
├── models/                       # Created during training
├── app.py                        # Streamlit demonstration
├── train.py                      # Reproducible training workflow
├── HeartdiseaseFinal.ipynb        # Original exploratory notebook
├── requirements.txt
└── README.md
```

## Run locally

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Install:
```bash
pip install -r requirements.txt
```

Train and save the model:
```bash
python train.py
```

Launch the demo:
```bash
streamlit run app.py
```

The training script creates `models/heart_disease_pipeline.joblib`. Train before launching the app.

## Evaluation

The script reports:
- **Accuracy:** overall fraction of correct holdout predictions.
- **F1:** balance between precision and recall for the positive class.
- **ROC-AUC:** ranking discrimination across classification thresholds.
- **Classification report:** precision, recall, F1 and support for each class.

No performance score is promised in advance; use the values printed by your own run.

## Limitations

- The dataset may contain sampling bias and does not represent every population.
- The model has not been clinically validated and is not suitable for real-world medical use.
- A holdout score on this dataset does not establish safety, fairness, or generalization to patients.
- The app is a demonstration of model deployment only, not a healthcare service.

## Tech stack

Python, Pandas, Scikit-learn, Joblib and Streamlit.
