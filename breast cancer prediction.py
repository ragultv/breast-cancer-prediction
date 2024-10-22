import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.base import TransformerMixin
import matplotlib.pyplot as plt

# Define the corrected SigmoidTransformer class
class SigmoidTransformer(TransformerMixin):
    def __init__(self, model):
        self.model = model

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        sigmoid_values = self.model.predict_proba(X)[:, 1]  # Probability of class 1 (breast cancer)
        return sigmoid_values.reshape(-1, 1)

# Load data from Excel
data_path = r"C:\Users\tragu\Downloads\archive\sample_data.xlsx"
data = pd.read_excel(data_path, engine='openpyxl')

# Drop rows with missing values
data.dropna(inplace=True)

# Define features and target variable
selected_features = ['smoker', 'alcoholic', 'pregnant']
target_variable = 'breast cancer'

# Select the features and target variable from the DataFrame
features = data[selected_features]
target = data[target_variable]

# Create a pipeline with an imputer transformer and logistic regression model
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),  # Impute missing values using mean strategy
    ('logreg', LogisticRegression())
])

# Train the logistic regression model using the pipeline
pipeline.fit(features, target)

# Create a pipeline with SigmoidTransformer for obtaining sigmoid values
pipeline_with_sigmoid = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),  # Fit imputer on training data
    ('logreg', pipeline.named_steps['logreg']),
    ('sigmoid', SigmoidTransformer(pipeline.named_steps['logreg']))
])

# Fit the imputer on the training data
pipeline_with_sigmoid.named_steps['imputer'].fit(features)

# Generate features for all IDs from 1 to 10
all_ids = np.arange(1, 11)
features_all_ids = pd.DataFrame({'ID': all_ids})
features_all_ids[selected_features] = np.tile(data[selected_features].mean().values.reshape(1, -1), (len(all_ids), 1))
  # Filling missing values with mean

# Predict the probabilities of breast cancer for all IDs
probas_all_ids = pipeline.predict_proba(features_all_ids[selected_features])[:, 1]

# Predict the sigmoid values of breast cancer for all IDs
sigmoid_values_all_ids = pipeline_with_sigmoid.named_steps['sigmoid'].transform(features_all_ids[selected_features])

# Create DataFrames with IDs, probabilities, and sigmoid values
result_df_all = pd.DataFrame({'Person_ID': all_ids, 'Probability': probas_all_ids, 'Sigmoid_Value': sigmoid_values_all_ids.flatten()})

# Print or display the DataFrame with probabilities and sigmoid values
print("Predicted probabilities and sigmoid values of breast cancer for all IDs:")
print(result_df_all[['Person_ID', 'Probability', 'Sigmoid_Value']])

# Evaluate the model using accuracy, precision, recall, and F1 score
X_test = features.iloc[:10]  # Test the model on the first 100 rows of the data
y_test = target.iloc[:10]
y_pred = pipeline.predict(X_test)
print("Model Evaluation Metrics:")
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

# Plot the sigmoid function curve
x_values = np.linspace(-10, 10, 1000)
sigmoid_curve = 1 / (1 + np.exp(-x_values))

plt.figure(figsize=(10, 6))
plt.plot(x_values, sigmoid_curve, label='Sigmoid Function', color='blue')

# Plot the breast cancer predictions for each ID
plt.scatter(sigmoid_values_all_ids, probas_all_ids, label='Breast Cancer Predictions', color='red')
for i, txt in enumerate(all_ids):
    plt.annotate(txt, (sigmoid_values_all_ids[i], probas_all_ids[i]))

plt.xlabel('Sigmoid Value')
plt.ylabel('Probability of Breast Cancer')
plt.title('Sigmoid Function and Breast Cancer Predictions')
plt.legend()
plt.grid(True)
plt.show()
