# Customer Churn Prediction

A machine learning project that predicts whether a customer is likely to churn based on customer and subscription-related information.

## Models Used

* Logistic Regression
* Decision Tree
* Random Forest

## Features

* Age
* Gender
* Tenure
* Usage Frequency
* Support Calls
* Payment Delay
* Subscription Type
* Contract Length
* Total Spend
* Last Interaction

`CustomerID` was removed because it is only an identifier.

## Workflow

```text
Data Cleaning
     ↓
Feature Preprocessing
     ↓
80/20 Stratified Split
     ↓
Train Models
     ↓
Model Evaluation
     ↓
Compare Models
```

## Results

| Model               | Accuracy |
| ------------------- | -------: |
| Logistic Regression |   89.47% |
| Decision Tree       |    ~100% |
| Random Forest       |    ~100% |

Evaluation metrics used:

* Accuracy
* Precision
* Recall
* F1 Score

## Dataset Observation

The original Kaggle train and test datasets have different feature and churn distributions. Because of this, the models performed significantly differently on the original Kaggle test data.

This project therefore also demonstrates the importance of checking **data distribution and model generalization**, rather than relying only on accuracy.

## Tech Stack

Python • Pandas • NumPy • Scikit-learn • Matplotlib • Jupyter Notebook

## Future Improvements

* Hyperparameter tuning
* Cross-validation
* Feature importance
* ROC-AUC
* Streamlit deployment
