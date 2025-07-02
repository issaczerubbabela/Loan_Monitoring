import streamlit as st
import pandas as pd
import os

# Dummy function to simulate your SERP API search
def perform_web_search(borrower_info, selected_attributes):
    os.makedirs('articles', exist_ok=True)
    filename = f'articles/{borrower_info["borrower_id"]}_articles.txt'
    with open(filename, 'w') as f:
        f.write(f"Simulated articles for {borrower_info['borrower_name']} with attributes {selected_attributes}")
    return filename

st.title("Borrower Risk Assessment Web Search Tool")

st.sidebar.header("Input Mode")
input_mode = st.sidebar.radio("Choose Input Mode:", ("Manual Form", "Upload CSV File"))

# Common checkboxes for attributes to query
st.subheader("Attributes to Query (checkboxes)")

attr_financial_health = st.checkbox("Financial Health")
attr_employer_reputation = st.checkbox("Employer Reputation")
attr_industry_trends = st.checkbox("Industry Trends")
attr_social_media_sentiment = st.checkbox("Social Media Sentiment")
attr_litigation_history = st.checkbox("Litigation History")

selected_attributes = []
if attr_financial_health:
    selected_attributes.append("Financial Health")
if attr_employer_reputation:
    selected_attributes.append("Employer Reputation")
if attr_industry_trends:
    selected_attributes.append("Industry Trends")
if attr_social_media_sentiment:
    selected_attributes.append("Social Media Sentiment")
if attr_litigation_history:
    selected_attributes.append("Litigation History")

if input_mode == "Manual Form":
    st.subheader("Borrower Information Form")

    with st.form("borrower_form"):
        borrower_id = st.text_input("Borrower ID")
        borrower_name = st.text_input("Borrower Name")
        loan_amount = st.number_input("Loan Amount", min_value=0.0, step=1000.0, format="%.2f")
        loan_start_year = st.number_input("Loan Start Year", min_value=1900, max_value=2100, step=1)
        job_title = st.text_input("Job Title")
        company = st.text_input("Company")
        industry = st.text_input("Industry")
        repayments_on_time = st.number_input("Repayments On Time", min_value=0, step=1)
        late_payments = st.number_input("Late Payments", min_value=0, step=1)
        avg_days_late = st.number_input("Average Days Late", min_value=0.0, step=1.0)
        age = st.number_input("Age", min_value=0, step=1)
        location = st.text_input("Location")

        submitted = st.form_submit_button("Submit and Search")

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

        st.write("Performing web search for single borrower...")
        article_file = perform_web_search(borrower_info, selected_attributes)
        st.success(f"Articles saved to: {article_file}")

else:
    st.subheader("Upload Borrower CSV File")

    csv_file = st.file_uploader("Upload CSV", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)

        # Show preview
        st.write("CSV Preview:")
        st.dataframe(df)

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

                # Call your SERP API function
                article_file = perform_web_search(borrower_info, selected_attributes)
                st.write(f"Processed Borrower ID {borrower_info['borrower_id']}: Articles saved to {article_file}")

            st.success("Completed web search for all borrowers in CSV.")
