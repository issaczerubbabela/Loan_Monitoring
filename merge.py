import pandas as pd
import json

# Paths
csv_file_path = "./your_uploaded_borrower_file.csv"
response_file_path = "./responses/response.txt"
output_csv_path = "./processed/processed_borrower.csv"

# Load CSV
df = pd.read_csv(csv_file_path)

# Read and parse response.txt
with open(response_file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the "json" word from the start
if content.startswith("json"):
    json_str = content[len("json"):].strip()
else:
    json_str = content

# Load JSON
response_json = json.loads(json_str)

# Create a dictionary to hold criticality values
criticality_dict = {}
for attr, info in response_json.items():
    criticality_dict[attr] = info.get("criticality", "")

# Add new columns to DataFrame (one per attribute)
for attr_name, crit_value in criticality_dict.items():
    # You can optionally make column names simpler if needed
    col_name = attr_name.strip()
    df[col_name] = crit_value

# Save combined CSV
df.to_csv(output_csv_path, index=False)
print(f"✅ Combined CSV saved to: {output_csv_path}")
