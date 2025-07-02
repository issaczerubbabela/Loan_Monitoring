import pandas as pd
from main_serp import generate_queries, search_and_save

SERPAPI_API_KEY = "YOUR_SERPAPI_KEY"

QUERY_KEYS = [
    "Stock performance outlook",
    "Industry recession/growth",
    "Job automation risk",
    "Job market demand",
    "Company M&A possibility",
    "Product relevance",
    "Skill obsolescence",
    "Replaceability risk",
    "Pollution projection",
    "Disease risk in polluted zones",
    "College education cost",
    "Financial burden of children"
]

KEY_TO_INDEX = {k: i for i, k in enumerate(QUERY_KEYS)}

def process_csv(filepath, selected_keys, years_ahead=5):
    df = pd.read_csv(filepath)
    for idx, row in df.iterrows():
        borrower_info = {
            "borrower_id": str(row["borrower_id"]),
            "job_title": row["job_title"],
            "company": row["company"],
            "industry": row["industry"]
        }

        queries = generate_queries(
            borrower_info["job_title"],
            borrower_info["company"],
            borrower_info["industry"],
            years_ahead
        )
        selected_queries = [queries[KEY_TO_INDEX[key]] for key in selected_keys]

        for query in selected_queries:
            saved_files = search_and_save(query, borrower_info["borrower_id"], SERPAPI_API_KEY)
            print(f"Borrower {borrower_info['borrower_id']} - Saved {len(saved_files)} articles.")

if __name__ == "__main__":
    # Example usage
    csv_file = "loan_data.csv"
    selected_keys = QUERY_KEYS  # or choose a subset
    process_csv(csv_file, selected_keys, years_ahead=5)
