import pandas as pd
import json

def merge_csv_with_text_json(csv_file_path, response_file_path, output_file_path):
    # List of attribute columns (ordered)
    attribute_columns = [
        "stock_performance_outlook",
        "industry_recession_or_growth",
        "company_M_and_A_possibility",
        "job_automation_risk",
        "job_market_demand",
        "product_relevance",
        "replaceability_risk",
        "pollution_projection",
        "disease_risk_polluted_zone",
        "financial_burden_children"
    ]

    # Load CSV
    df = pd.read_csv(csv_file_path)

    # Read response.txt
    with open(response_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove "json" word
    if content.startswith("json"):
        json_str = content[len("json"):].strip()
    else:
        json_str = content

    # Load as JSON object
    response_json = json.loads(json_str)

    # Get criticality values in order
    criticality_values = []
    for key in response_json:
        crit = response_json[key].get("criticality", "")
        criticality_values.append(crit)

    # Check number of attributes matches
    if len(criticality_values) != len(attribute_columns):
        raise ValueError("Number of attributes in response does not match expected attribute columns!")

    # Add each attribute column to the CSV DataFrame
    for attr_name, crit_value in zip(attribute_columns, criticality_values):
        df[attr_name] = crit_value

    # Save merged CSV
    df.to_csv(output_file_path, index=False)
    print(f"✅ Combined CSV saved to: {output_file_path}")

# Example usage
if __name__ == "__main__":
    csv_file_path = "./your_uploaded_borrower_file.csv"
    response_file_path = "./responses/response.txt"
    output_file_path = "./processed/processed_borrower.csv"

    merge_csv_with_text_json(csv_file_path, response_file_path, output_file_path)
