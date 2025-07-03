import pandas as pd
import numpy as np
import random

# Seed for reproducibility
np.random.seed(42)

# Possible values
categories = ['Low', 'Medium', 'High']
industries = ['Tech', 'Finance', 'Healthcare', 'Education', 'Manufacturing']
locations = ['New York', 'San Francisco', 'Chicago', 'Boston', 'Austin']

def generate_categorical_score(val):
    if val == 'Low':
        return 1
    elif val == 'Medium':
        return 0
    else:
        return -1

records = []

for i in range(1, 101):
    borrower_id = i
    borrower_name = f'Borrower_{i}'
    loan_amount = np.random.randint(5000, 100000)
    loan_start_year = np.random.randint(2010, 2024)
    job_title = random.choice(['Engineer', 'Manager', 'Analyst', 'Teacher', 'Nurse'])
    company = f'Company_{np.random.randint(1, 20)}'
    industry = random.choice(industries)
    repayments_on_time = np.random.randint(10, 60)
    late_payments = np.random.randint(0, 10)
    average_days_late = np.random.randint(0, 30)
    age = np.random.randint(21, 65)
    location = random.choice(locations)
    
    # Categorical criticality attributes
    stock_performance_outlook = random.choice(categories)
    industry_recession_or_growth = random.choice(categories)
    company_M_and_A_possibility = random.choice(categories)
    job_automation_risk = random.choice(categories)
    job_market_demand = random.choice(categories)
    product_relevance = random.choice(categories)
    skilled_obsolescence = random.choice(categories)
    replaceability_risk = random.choice(categories)
    pollution_projection = random.choice(categories)
    disease_risk_polluted_zone = random.choice(categories)
    college_education_cost = np.random.randint(10000, 50000)
    financial_burden_children = random.choice(categories)
    
    # Score calculation
    score = 0
    
    score += (repayments_on_time / 10)  # more on-time payments = better
    score -= (late_payments * 0.5)
    score -= (average_days_late * 0.2)
    
    score += generate_categorical_score(job_market_demand) * 2
    score += generate_categorical_score(product_relevance) * 2
    score -= generate_categorical_score(job_automation_risk)
    score -= generate_categorical_score(skilled_obsolescence)
    score -= generate_categorical_score(replaceability_risk)
    score += generate_categorical_score(stock_performance_outlook)
    score -= generate_categorical_score(company_M_and_A_possibility)
    score -= generate_categorical_score(industry_recession_or_growth)
    score -= generate_categorical_score(financial_burden_children)
    
    # Normalize final score to [-2, 2]
    if score >= 6:
        label = 2
    elif score >= 3:
        label = 1
    elif score >= 0:
        label = 0
    elif score >= -3:
        label = -1
    else:
        label = -2

    # Append record
    records.append([
        borrower_id, borrower_name, loan_amount, loan_start_year, job_title,
        company, industry, repayments_on_time, late_payments, average_days_late,
        age, location, stock_performance_outlook, industry_recession_or_growth,
        company_M_and_A_possibility, job_automation_risk, job_market_demand,
        product_relevance, skilled_obsolescence, replaceability_risk,
        pollution_projection, disease_risk_polluted_zone, college_education_cost,
        financial_burden_children, label
    ])

# Column names
columns = [
    'borrower_id', 'borrower_name', 'loan_amount', 'loan_start_year', 'job_title',
    'company', 'industry', 'repayments_on_time', 'late_payments', 'average_days_late',
    'age', 'location', 'stock_performance_outlook', 'industry_recession_or_growth',
    'company_M_and_A_possibility', 'job_automation_risk', 'job_market_demand',
    'product_relevance', 'skilled_obsolescence', 'replaceability_risk',
    'pollution_projection', 'disease_risk_polluted_zone', 'college_education_cost',
    'financial_burden_children', 'loan_repayment_likelihood'
]

# Create DataFrame
df = pd.DataFrame(records, columns=columns)

# Save to CSV
df.to_csv('borrowers.csv', index=False)

print("✅ Sample data generated and saved as 'borrowers.csv'")
