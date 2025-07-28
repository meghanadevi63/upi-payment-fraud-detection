import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import cross_val_score

# Load the dataset (you need to replace this with the actual file path or link)
df = pd.read_csv('synthetic_upi_fraud_dataset.csv')

# Preprocessing: Removing the `upi_id` as it is not a feature for prediction
df = df.drop('upi_id', axis=1)

# Define features (X) and target (y)
X = df.drop('is_fraud', axis=1)
y = df['is_fraud']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Apply scaling (StandardScaler)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Handling class imbalance using SMOTE (Synthetic Minority Over-sampling Technique)
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)

# Initialize the model (RandomForestClassifier)
rf_model = RandomForestClassifier(random_state=42)

# Hyperparameter tuning using GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}
grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)

# Fit the model on the training data with cross-validation
grid_search.fit(X_train_resampled, y_train_resampled)
best_model = grid_search.best_estimator_

# Predict on the test set
y_pred = best_model.predict(X_test_scaled)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

# Display metrics
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"Confusion Matrix:\n{conf_matrix}")

# Evaluate the model's cross-validation score
cross_val_accuracy = cross_val_score(best_model, X_train_resampled, y_train_resampled, cv=5)
print(f"Cross-validation accuracy: {cross_val_accuracy.mean():.4f}")

# Ensure new_data has the same columns as X_train
new_data = pd.DataFrame({
    'account_age_days': [103],
    'transaction_count_last_24h': [11],
    'transaction_velocity_1h': [7],
    'average_transaction_amount': [87672],
    'average_transaction_interval': [10.25],
    'device_change': [0],
    'transaction_amount': [2062],
    'new_recipient': [0],
    'similar_transactions_last_10min': [2],
    'location_change': [0],
    'ip_address_change': [1],
    'vpn_usage': [0],
    'transaction_time': [0],
    'merchant_transaction': [0],
    'blacklist_flag': [1]
})

# Ensure the same order of columns as the training set
new_data = new_data[X.columns]

# Now, apply scaling using the same scaler that was fitted during training
new_data_scaled = scaler.transform(new_data)

# Predict the fraud for new data
new_prediction = best_model.predict(new_data_scaled)

print(f"Predicted fraud for the new data: {new_prediction[0]}")
import pickle

# Save the trained model
with open("rf_model.pkl", "wb") as model_file:
    pickle.dump(best_model, model_file)

# Save the scaler
with open("scaler.pkl", "wb") as scaler_file:
    pickle.dump(scaler, scaler_file)

print("✅ Model and scaler saved successfully!")

