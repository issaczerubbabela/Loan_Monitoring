import pandas as pd
import json
import os

def merge_csv_with_text_json(csv_path, text_folder, output_csv_path):
    # Load CSV
    df = pd.read_csv(csv_path)

    attributes = [
        "stock_performance_outlook", "industry_recession_or_growth", "company_M_and_A_possibility",
        "job_automation_risk", "job_market_demand", "product_relevance",
        "skilled_obsolescence", "replaceability_risk", "pollution_projection",
        "disease_risk_polluted_zone", "college_education_cost", "financial_burden_children"
    ]

    # Add columns for each attribute (just criticality)
    for attr in attributes:
        df[attr] = ""

    for idx, row in df.iterrows():
        borrower_id = str(row["borrower_id"])

        # File assumed to be named <borrower_id>.txt inside text_folder
        text_file_path = os.path.join(text_folder, f"{borrower_id}.txt")

        if os.path.exists(text_file_path):
            with open(text_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove the first "JSON" line if it exists
            if content.startswith("JSON"):
                json_str = content[4:].strip()
            else:
                json_str = content.strip()

            try:
                data = json.loads(json_str)

                for attr in attributes:
                    if attr in data:
                        df.at[idx, attr] = data[attr]
            except json.JSONDecodeError:
                print(f"⚠️ Error decoding JSON for borrower ID {borrower_id}")

        else:
            print(f"⚠️ Text file not found for borrower ID {borrower_id}")

    # Save new combined CSV
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Combined CSV saved to: {output_csv_path}")

# Example usage:
# merge_csv_with_text_json("borrowers.csv", "responses_folder", "borrowers_combined.csv")
