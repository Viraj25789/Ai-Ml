# Ford Car Price Prediction

A simple machine learning project that explores Ford used-car data and predicts car prices using **Linear Regression**.

The project includes basic **Exploratory Data Analysis (EDA)**, categorical encoding, feature scaling, train/test splitting, model training, and evaluation using **R²** and **Adjusted R²**.

## Project Overview

The dataset contains Ford used-car information such as:

- Model
- Year
- Price
- Transmission
- Mileage
- Fuel Type
- Tax
- MPG
- Engine Size

The target variable is **`price`**.

## Workflow

1. Load the Ford car dataset using Pandas.
2. Inspect the dataset using `head()`, `info()`, `describe()`, and shape/null-value checks.
3. Perform EDA using Matplotlib and Seaborn.
4. Encode categorical features using:
   - One-hot encoding
   - Label encoding
5. Scale numerical features using `StandardScaler`.
6. Split the data into training and testing sets.
7. Train a Linear Regression model.
8. Make predictions on the test data.
9. Evaluate the model using:
   - R² Score
   - Adjusted R² Score

## Project Structure

```text
ford-car-price-prediction/
│
├── data/
│   └── ford.csv
│
├── main.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter Notebook

## Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
cd ford-car-price-prediction
```

Create and activate a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project

Start Jupyter Notebook:

```bash
jupyter notebook
```

Open:

```text
main.ipynb
```

Then run the notebook cells from top to bottom.

## Model

The project uses **Linear Regression** to predict the price of Ford cars.

Two approaches for categorical variables are explored:

1. **One-Hot Encoding**
2. **Label Encoding**

The numerical features are scaled using `StandardScaler`.

## Evaluation

The model is evaluated using:

**R² Score**
Measures how well the model explains variation in the target price.

**Adjusted R²**
Provides an adjusted version of R² that considers the number of input features used by the model.

## features

- Data loading and inspection
- Data cleaning basics
- Exploratory Data Analysis
- Feature encoding
- Feature scaling
- Train/test splitting
- Linear Regression
- Model evaluation
