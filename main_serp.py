import os
import requests
from bs4 import BeautifulSoup

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

def search_and_save(query, borrower_id, serpapi_api_key, attribute_key, clean=True):
    os.makedirs("articles/html", exist_ok=True)
    os.makedirs("articles/clean", exist_ok=True)

    params = {
        "q": query,
        "api_key": serpapi_api_key,
        "engine": "google",
        "num": "5"
    }

    response = requests.get("https://serpapi.com/search", params=params, verify=False)
    data = response.json()

    saved_files = []

    if "organic_results" in data:
        for idx, result in enumerate(data["organic_results"][:3]):
            link = result.get("link")
            if link:
                try:
                    page = requests.get(link, timeout=10, verify=False)
                    raw_html = page.text

                    html_filename = f"articles/html/{borrower_id}_{attribute_key}_{idx+1}.html"
                    with open(html_filename, "w", encoding="utf-8") as f:
                        f.write(raw_html)

                    if clean:
                        clean_filename = clean_file(html_filename, borrower_id, attribute_key, idx+1)
                        saved_files.append(clean_filename)
                    else:
                        saved_files.append(html_filename)
                except Exception as e:
                    print(f"Failed to fetch content from {link}: {e}")

    return saved_files

def clean_file(html_path, borrower_id, attribute_key, idx):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = "\n".join(lines)

    clean_filename = f"articles/clean/{borrower_id}_{attribute_key}_{idx}.txt"
    with open(clean_filename, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"Cleaned text saved: {clean_filename}")
    return clean_filename
