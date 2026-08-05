from sklearn.ensemble import  RandomForestClassifier
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Load the training data
data = pd.read_csv('practice_code/test_data/train.csv')

# Initialize the Random Forest Classifier
clf = RandomForestClassifier()

X_train = data.iloc[:, :-1]
Y_train = data.iloc[:, -1]

# Train the model
train = clf.fit(X_train, Y_train)

# Load the test data
test = pd.read_csv('practice_code/test_data/test.csv')
test_X = test.iloc[:, :-1]

# Make predictions on the test data
predictions = train.predict(test_X)

# Create a DataFrame to store the predictions
df = pd.DataFrame(predictions, columns=['Predicted'])

# Evaluate the model's performance
count=0

for i in range(len(predictions)):
    if df.iloc[i, 0] == test['species'].iloc[i]:
        count += 1
    else:
        logging.info(f"Not Matched Data - Predicted: {df.iloc[i, 0]}, Actual: {test['species'].iloc[i]}")

logging.info(f"Total correct predictions: {count}/{len(predictions)}")

# Calculate accuracy percentage
accuracy_percentage = (count*100) / len(predictions)
logging.info(f"Accuracy: {accuracy_percentage}%")


