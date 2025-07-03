import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

# -------------------------
# Load data
# -------------------------
train_df = pd.read_csv('borrowers_train.csv')
test_df = pd.read_csv('borrowers_test.csv')

# Drop descriptive string columns
drop_cols = ['borrower_id', 'borrower_name', 'job_title', 'company', 'industry', 'location']
X_train = train_df.drop(columns=drop_cols + ['loan_repayment_likelihood'])
y_train = train_df['loan_repayment_likelihood']

X_test = test_df.drop(columns=drop_cols + ['loan_repayment_likelihood'])
y_test = test_df['loan_repayment_likelihood']

# -------------------------
# Encode Low/Medium/High columns
# -------------------------
cat_cols = ['stock_performance_outlook', 'industry_recession_or_growth',
            'company_M_and_A_possibility', 'job_automation_risk',
            'job_market_demand', 'product_relevance', 'skilled_obsolescence',
            'replaceability_risk', 'pollution_projection',
            'disease_risk_polluted_zone', 'financial_burden_children']

le = LabelEncoder()
for col in cat_cols:
    X_train[col] = le.fit_transform(X_train[col])
    X_test[col] = le.transform(X_test[col])

# -------------------------
# Train XGBoost classifier
# -------------------------
model = xgb.XGBClassifier(objective='multi:softprob', num_class=5, eval_metric='mlogloss', use_label_encoder=False, random_state=42)
model.fit(X_train, y_train)

# -------------------------
# Predict probabilities and final prediction
# -------------------------
y_prob = model.predict_proba(X_test)
y_pred = model.predict(X_test)

# -------------------------
# Evaluation
# -------------------------
print("Classification Report:\n")
print(classification_report(y_test, y_pred))

# Confusion matrix plot
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=[-2, -1, 0, 1, 2], yticklabels=[-2, -1, 0, 1, 2])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

# -------------------------
# Show probabilities for first 5 test samples (example)
# -------------------------
print("\nSample prediction probabilities for first 5 borrowers:\n")
for i in range(5):
    print(f"Borrower {i+1}: {y_prob[i]}")

# -------------------------
# Feature importance plot
# -------------------------
xgb.plot_importance(model, max_num_features=10, importance_type='gain', title='Top 10 Feature Importances')
plt.show()

# If you'd like a seaborn barplot style, we can also do:
importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values(by='importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='importance', y='feature', data=importance_df.head(10))
plt.title("Top 10 Feature Importances (by XGBoost)")
plt.show()
