import pandas as pd
import requests
import json
from google.generativeai import configure, GenerativeModel
from serpapi import GoogleSearch
from keys import GEMINI_KEY, SERP_KEY
import time

# --------------------- Gemini API Setup ---------------------
configure(api_key=GEMINI_KEY)
SERPAPI_KEY = SERP_KEY
gemini = GenerativeModel("gemini-2.5-flash")

# --------------------- Load Borrower Data ---------------------
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

# --------------------- Web Search Agent ---------------------
def generate_queries(job_title, company, industry):
    queries = [
        f"{company} stock performance future outlook",
        f"{industry} recession or growth prediction",
        f"{job_title} automation risk",
        f"{industry} job market demand 2025",
        f"{company} acquisition merger news",
        f"{company} product relevance 2030",
        f"{job_title} skill obsolescence trend"
    ]
    return queries

# Dummy search for now
def search_web(query, num_results=3):
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": SERPAPI_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    articles = []
    try:
        for res in results.get("organic_results", [])[:num_results]:
            title = res.get("title", "")
            link = res.get("link", "")
            snippet = res.get("snippet", "")
            articles.append(f"{title}\n{snippet}\n{link}")
    except Exception as e:
        print(f"Error fetching results: {e}")

    # Be polite to the API
    time.sleep(1)

    return "\n\n".join(articles)  # Replace with real search API (SerpAPI or scraping)

# --------------------- Gemini Summarizer ---------------------
def summarize_external_signals(company, job, industry, raw_texts):
    full_prompt = f"""
Act as a financial analyst. Based on the information below, assess the following for {job} at {company} in the {industry} industry:
- Company stock trend
- Industry recession risk
- Automation risk for the role
- Acquisition/Merger likelihood
- Skill relevance
- Product demand future

TEXTS:
{raw_texts}
"""
    response = gemini.generate_content(full_prompt)
    return response.text

# --------------------- Feature Extraction ---------------------
def extract_features_from_summary(summary_text):
    prompt = f"""
Extract the following as structured JSON (keys: stock_projection, industry_health, automation_risk, acquisition_risk, skill_relevance, product_demand) from this:
{summary_text}
"""
    response = gemini.generate_content(prompt)
    try:
        return json.loads(response.text)
    except:
        print("Parsing failed. Raw response:")
        print(response.text)
        return {}

# --------------------- Scoring Function ---------------------
def compute_risk_score(features):
    score = 0
    if features.get("automation_risk") == "high":
        score += 2
    if features.get("stock_projection") == "negative":
        score += 2
    if features.get("industry_health") == "shrinking":
        score += 1
    if features.get("skill_relevance") == "obsolete":
        score += 2
    return score

# --------------------- Main Pipeline ---------------------
def process_borrower(row):
    queries = generate_queries(row['job_title'], row['company'], row['industry'])
    raw_info = "\n".join([search_web(q) for q in queries])
    summary = summarize_external_signals(row['company'], row['job_title'], row['industry'], raw_info)
    features = extract_features_from_summary(summary)
    risk_score = compute_risk_score(features)
    return risk_score, summary

if __name__ == "__main__":
    df = load_data("loan_data.csv")
    df['risk_score'], df['explanation'] = zip(*df.apply(process_borrower, axis=1))
    df.to_csv("repayability_results.csv", index=False)
    print("Done. Output saved to repayability_results.csv")
