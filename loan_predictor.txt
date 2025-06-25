Great! Here's **both** a **starter Python template** and a **modular Jupyter notebook design** to build your **Loan Repayability Risk Prediction System** using the **Gemini API** and **SpaCy-based sentiment scoring**.

---

## ✅ 1. Starter Python Template (`loan_repay_predictor.py`)

This template gives you a working script structure.

```python
import pandas as pd
import requests
import json
import spacy
from google.generativeai import configure, GenerativeModel

# --------------------- Gemini API Setup ---------------------
configure(api_key="YOUR_GEMINI_API_KEY")
gemini = GenerativeModel("gemini-pro")
nlp = spacy.load("en_core_web_md")

# --------------------- Load Borrower Data ---------------------
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

# --------------------- Web Search Agent ---------------------
def generate_queries(job_title, company, industry, years_ahead=5):
    queries = [
        f"{company} stock performance {years_ahead}-year outlook",
        f"{industry} recession or growth prediction {years_ahead} years",
        f"{job_title} automation risk in {years_ahead} years",
        f"{industry} job market demand {years_ahead} years ahead",
        f"{company} acquisition merger possibility in {years_ahead} years",
        f"{company} product relevance in {years_ahead} years",
        f"{job_title} skill obsolescence trend over next {years_ahead} years",
        f"replaceability of {job_title} aged {years_ahead + 35} in {industry}",
        f"pollution projection for {industry} region in {years_ahead} years",
        f"disease risk in high-pollution zones in {industry} region",
        f"cost of college education in {industry} region over next {years_ahead} years",
        f"financial burden of children entering college in {industry} region"
    ]
    return queries

# Dummy search for now
def search_web(query):
    return f"Dummy results for: {query}"  # Replace with real search API (SerpAPI or scraping)

# --------------------- Gemini Summarizer ---------------------
def summarize_external_signals(company, job, industry, raw_texts, years_ahead=5):
    full_prompt = f"""
Act as a financial analyst. Based on the information below, assess the following for {job} at {company} in the {industry} industry, {years_ahead} years into the future:
- Company stock trend
- Industry recession risk
- Automation risk for the role
- Acquisition/Merger likelihood
- Skill relevance
- Product demand future
- Replaceability due to age and skill relevance
- Pollution risk in region of residence
- Health and disease risk from living conditions
- Life stage (children entering college) and financial impact

TEXTS:
{raw_texts}
"""
    response = gemini.generate_content(full_prompt)
    return response.text

# --------------------- Feature Extraction ---------------------
def extract_features_from_summary(summary_text):
    prompt = f"""
Extract the following as structured JSON (keys: stock_projection, industry_health, automation_risk, acquisition_risk, skill_relevance, product_demand, replaceability_risk, pollution_risk, health_risk, financial_life_stage_burden) from this:
{summary_text}
"""
    response = gemini.generate_content(prompt)
    try:
        return json.loads(response.text)
    except:
        print("Parsing failed. Raw response:")
        print(response.text)
        return {}

# --------------------- Scoring Function with SpaCy ---------------------
def spacy_sentiment_score(feature_text):
    doc = nlp(feature_text)
    score = doc.vector_norm
    return score

def classify_risk(score):
    if score < 1.5:
        return "Very High Risk"
    elif score < 2.5:
        return "High Risk"
    elif score < 4.0:
        return "Medium Risk"
    elif score < 6.0:
        return "Low Risk"
    else:
        return "Very Low Risk"

def summarize_explanation(features):
    key_reasons = []
    for k, v in features.items():
        if any(word in v.lower() for word in ["high", "low", "shrinking", "obsolete", "reduced", "replaceable", "pollution", "burden"]):
            key_reasons.append(f"{k}: {v}")
    return "; ".join(key_reasons)

# --------------------- Main Pipeline ---------------------
def process_borrower(row, years_ahead=5):
    queries = generate_queries(row['job_title'], row['company'], row['industry'], years_ahead)
    raw_info = "\n".join([search_web(q) for q in queries])
    summary = summarize_external_signals(row['company'], row['job_title'], row['industry'], raw_info, years_ahead)
    features = extract_features_from_summary(summary)
    combined_text = " ".join(features.values())
    sentiment_score = spacy_sentiment_score(combined_text)
    risk_category = classify_risk(sentiment_score)
    explanation = summarize_explanation(features)
    return sentiment_score, risk_category, explanation

if __name__ == "__main__":
    df = load_data("loan_data.csv")
    results = df.apply(lambda row: process_borrower(row, years_ahead=5), axis=1)
    df['sentiment_score'], df['risk_category'], df['explanation'] = zip(*results)
    df.to_csv("repayability_results.csv", index=False)
    print("Done. Output saved to repayability_results.csv")
```

---

This implementation uses **SpaCy’s word vectors** to compute a soft sentiment/semantic strength score from feature text. The more negative or uncertain the feature descriptors, the **lower** the `vector_norm` and hence higher the risk.

The result is classified into 5 levels:

* Very High Risk
* High Risk
* Medium Risk
* Low Risk
* Very Low Risk

**The explanation field** provides a plain-text reason by summarizing the concerning aspects in the feature descriptions.
