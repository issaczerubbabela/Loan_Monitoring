import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Load data
train_df = pd.read_csv('borrowers_train.csv')
test_df = pd.read_csv('borrowers_test.csv')

# Drop non-numeric columns that are not useful for model
drop_cols = ['borrower_id', 'borrower_name', 'job_title', 'company', 'industry', 'location']
X_train = train_df.drop(columns=drop_cols + ['loan_repayment_likelihood'])
y_train = train_df['loan_repayment_likelihood']

X_test = test_df.drop(columns=drop_cols + ['loan_repayment_likelihood'])
y_test = test_df['loan_repayment_likelihood']

# Encode categorical (Low/Medium/High) columns numerically
cat_cols = ['stock_performance_outlook', 'industry_recession_or_growth',
            'company_M_and_A_possibility', 'job_automation_risk',
            'job_market_demand', 'product_relevance', 'skilled_obsolescence',
            'replaceability_risk', 'pollution_projection',
            'disease_risk_polluted_zone', 'financial_burden_children']

le = LabelEncoder()
for col in cat_cols:
    X_train[col] = le.fit_transform(X_train[col])
    X_test[col] = le.transform(X_test[col])

# Train XGBoost model
model = xgb.XGBClassifier(objective='multi:softmax', num_class=5, eval_metric='mlogloss', use_label_encoder=False)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("Classification Report:\n")
print(classification_report(y_test, y_pred))
