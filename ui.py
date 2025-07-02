import streamlit as st
import pandas as pd
import os

# Dummy function to simulate your SERP API search
def perform_web_search(borrower_info, selected_queries, years_ahead):
    os.makedirs('articles', exist_ok=True)
    filename = f'articles/{borrower_info["borrower_id"]}_articles.txt'

    # Simulate generating query list for this borrower
    queries = []
    company = borrower_info["company"]
    industry = borrower_info["industry"]
    job_title = borrower_info["job_title"]
    age = borrower_info["age"]

    if "Stock performance outlook" in selected_queries:
        queries.append(f"{company} stock performance {years_ahead}-year outlook")
    if "Industry recession/growth" in selected_queries:
        queries.append(f"{industry} recession or growth prediction {years_ahead} years")
    if "Job automation risk" in selected_queries:
        queries.append(f"{job_title} automation risk in {years_ahead} years")
    if "Job market demand" in selected_queries:
        queries.append(f"{industry} job market demand {years_ahead} years ahead")
    if "Company M&A possibility" in selected_queries:
        queries.append(f"{company} acquisition merger possibility in {years_ahead} years")
    if "Product relevance" in selected_queries:
        queries.append(f"{company} product relevance in {years_ahead} years")
    if "Skill obsolescence" in selected_queries:
        queries.append(f"{job_title} skill obsolescence trend over next {years_ahead} years")
    if "Replaceability risk" in selected_queries:
        queries.append(f"replaceability of {job_title} aged {years_ahead + 35} in {industry}")
    if "Pollution projection" in selected_queries:
        queries.append(f"pollution projection for {industry} region in {years_ahead} years")
    if "Disease risk in polluted zones" in selected_queries:
        queries.append(f"disease risk in high-pollution zones in {industry} region")
    if "College education cost" in selected_queries:
        queries.append(f"cost of college education in {industry} region over next {years_ahead} years")
    if "Financial burden of children" in selected_queries:
        queries.append(f"financial burden of children entering college in {industry} region")

    # Write simulated article file
    with open(filename, 'w') as f:
        f.write(f"Queries for {borrower_info['borrower_name']}:\n" + "\n".join(queries))
    return filename

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

        selected_queries = []
        if st.checkbox("Stock performance outlook"):
            selected_queries.append("Stock performance outlook")
        if st.checkbox("Industry recession/growth"):
            selected_queries.append("Industry recession/growth")
        if st.checkbox("Job automation risk"):
            selected_queries.append("Job automation risk")
        if st.checkbox("Job market demand"):
            selected_queries.append("Job market demand")
        if st.checkbox("Company M&A possibility"):
            selected_queries.append("Company M&A possibility")
        if st.checkbox("Product relevance"):
            selected_queries.append("Product relevance")
        if st.checkbox("Skill obsolescence"):
            selected_queries.append("Skill obsolescence")
        if st.checkbox("Replaceability risk"):
            selected_queries.append("Replaceability risk")
        if st.checkbox("Pollution projection"):
            selected_queries.append("Pollution projection")
        if st.checkbox("Disease risk in polluted zones"):
            selected_queries.append("Disease risk in polluted zones")
        if st.checkbox("College education cost"):
            selected_queries.append("College education cost")
        if st.checkbox("Financial burden of children"):
            selected_queries.append("Financial burden of children")

        if st.button("Submit and Search"):
            st.write("Performing web search for single borrower...")
            article_file = perform_web_search(borrower_info, selected_queries, years_ahead)
            st.success(f"Articles saved to: {article_file}")

else:
    st.subheader("Upload Borrower CSV File")

    csv_file = st.file_uploader("Upload CSV", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)

        st.write("CSV Preview:")
        st.dataframe(df)

        st.subheader("Select Query Attributes")

        selected_queries = []
        if st.checkbox("Stock performance outlook"):
            selected_queries.append("Stock performance outlook")
        if st.checkbox("Industry recession/growth"):
            selected_queries.append("Industry recession/growth")
        if st.checkbox("Job automation risk"):
            selected_queries.append("Job automation risk")
        if st.checkbox("Job market demand"):
            selected_queries.append("Job market demand")
        if st.checkbox("Company M&A possibility"):
            selected_queries.append("Company M&A possibility")
        if st.checkbox("Product relevance"):
            selected_queries.append("Product relevance")
        if st.checkbox("Skill obsolescence"):
            selected_queries.append("Skill obsolescence")
        if st.checkbox("Replaceability risk"):
            selected_queries.append("Replaceability risk")
        if st.checkbox("Pollution projection"):
            selected_queries.append("Pollution projection")
        if st.checkbox("Disease risk in polluted zones"):
            selected_queries.append("Disease risk in polluted zones")
        if st.checkbox("College education cost"):
            selected_queries.append("College education cost")
        if st.checkbox("Financial burden of children"):
            selected_queries.append("Financial burden of children")

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

                article_file = perform_web_search(borrower_info, selected_queries, years_ahead)
                st.write(f"Processed Borrower ID {borrower_info['borrower_id']}: Articles saved to {article_file}")

            st.success("Completed web search for all borrowers in CSV.")
