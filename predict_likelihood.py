import pandas as pd
import joblib

def prepare_features(df):
    # Drop columns you don't want
    df = df.drop(columns=[
        "borrower_id",
        "borrower_name",
        "job_title",
        "company",
        "industry",
        "location"
    ])

    # Encode categorical columns
    categorical_cols = [
        "stock_performance_outlook",
        "industry_recession_or_growth",
        "company_M_and_A_possibility",
        "job_automation_risk",
        "job_market_demand",
        "product_relevance",
        "skilled_obsolescence",
        "replaceability_risk",
        "pollution_projection",
        "disease_risk_polluted_zone",
        "financial_burden_children"
    ]

    for col in categorical_cols:
        df[col] = df[col].map({"Low": 0, "Medium": 1, "High": 2})

    return df

def main():
    # Path to processed CSV
    csv_path = "./processed/processed_borrower.csv"

    # Load CSV
    df = pd.read_csv(csv_path)

    # Save borrower ids and names for reference later
    borrower_info = df[["borrower_id", "borrower_name"]]

    # Prepare features
    X = prepare_features(df.copy())

    # Load trained model
    model = joblib.load("trained_model_xgb.pkl")

    # Predict likelihood
    predictions = model.predict(X)

    # Combine predictions with borrower info
    output_df = borrower_info.copy()
    output_df["repayment_likelihood"] = predictions

    # Save output to new CSV
    output_path = "./processed/borrower_predictions.csv"
    output_df.to_csv(output_path, index=False)

    print(f"✅ Predictions saved to {output_path}")
    print(output_df)

if __name__ == "__main__":
    main()
