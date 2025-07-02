import streamlit as st
import pandas as pd
import os
from main_serp import generate_queries  # Import your function

# Mapping keys to query list positions
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

def perform_web_search(borrower_info, selected_keys, years_ahead):
    os.makedirs('articles', exist_ok=True)
    filename = f'articles/{borrower_info["borrower_id"]}_articles.txt'

    job_title = borrower_info["job_title"]
    company = borrower_info["company"]
    industry = borrower_info["industry"]

    # Get all queries
    all_queries = generate_queries(job_title, company, industry, years_ahead)

    # Filter queries by user-selected keys
    selected_queries = [all_queries[KEY_TO_INDEX[key]] for key in selected_keys]

    with open(filename, 'w') as f:
        f.write(f"Queries for {borrower_info['borrower_name']}:\n" + "\n".join(selected_queries))
    return filename

# ---------------- Streamlit UI ----------------
st.title("Borrower Risk Assessment Web Search Tool")

st.sidebar.header("Input Mode")
input_mode = st.sidebar.radio("Choose Input Mode:", ("Manual Form", "Upload CSV File"))

years_ahead = st.sidebar.number_input("Years Ahead to Analyze", min_value=1, max_value=50, value=5)

if input_mode == "Manual Form":
    st.subheader("Borrower Information (Compact Form)")

    with st.form("borrower_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            borrower_id = st.text_input("Borrower ID")
        with col2:
            borrower_name = st.text_input("Name")
        with col3:
            age = st.number_input("Age", min_value=0, step=1)

        col4, col5, col6 = st.columns(3)
        with col4:
            loan_amount = st.number_input("Loan Amount", min_value=0.0, step=1000.0, format="%.2f")
        with col5:
            loan_start_year = st.number_input("Loan Start Year", min_value=1900, max_value=2100, step=1)
        with col6:
            location = st.text_input("Location")

        col7, col8 = st.columns(2)
        with col7:
            job_title = st.text_input("Job Title")
        with col8:
            company = st.text_input("Company")

        col9, col10 = st.columns(2)
        with col9:
            industry = st.text_input("Industry")
        with col10:
            repayments_on_time = st.number_input("Repayments On Time", min_value=0, step=1)

        col11, col12 = st.columns(2)
        with col11:
            late_payments = st.number_input("Late Payments", min_value=0, step=1)
        with col12:
            avg_days_late = st.number_input("Avg Days Late", min_value=0.0, step=1.0)

        submitted = st.form_submit_button("Next")

    if submitted:
        borrower_info = {
            "borrower_id": borrower_id,
            "borrower_name": borrower_name,
            "loan_amount": loan_amount,
            "loan_start_year": loan_start_year,
            "job_title": job_title,
            "company": company,
            "industry": industry,
            "repayments_on_time": repayments_on_time,
            "late_payments": late_payments,
            "avg_days_late": avg_days_late,
            "age": age,
            "location": location
        }

        st.subheader("Select Query Attributes")

        selected_keys = []
        for key in QUERY_KEYS:
            if st.checkbox(key):
                selected_keys.append(key)

        if st.button("Submit and Search"):
            st.write("Performing web search for single borrower...")
            article_file = perform_web_search(borrower_info, selected_keys, years_ahead)
            st.success(f"Articles saved to: {article_file}")

else:
    st.subheader("Upload Borrower CSV File")

    csv_file = st.file_uploader("Upload CSV", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)

        st.write("CSV Preview:")
        st.dataframe(df)

        st.subheader("Select Query Attributes")

        selected_keys = []
        for key in QUERY_KEYS:
            if st.checkbox(key):
                selected_keys.append(key)

        if st.button("Submit and Search for All Borrowers"):
            for idx, row in df.iterrows():
                borrower_info = {
                    "borrower_id": str(row["borrower_id"]),
                    "borrower_name": row["borrower_name"],
                    "loan_amount": row["loan_amount"],
                    "loan_start_year": row["loan_start_year"],
                    "job_title": row["job_title"],
                    "company": row["company"],
                    "industry": row["industry"],
                    "repayments_on_time": row["repayments_on_time"],
                    "late_payments": row["late_payments"],
                    "avg_days_late": row["avg_days_late"],
                    "age": row["age"],
                    "location": row["location"]
                }

                article_file = perform_web_search(borrower_info, selected_keys, years_ahead)
                st.write(f"Processed Borrower ID {borrower_info['borrower_id']}: Articles saved to {article_file}")

            st.success("Completed web search for all borrowers in CSV.")
