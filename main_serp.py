import os
import requests
from serpapi import GoogleSearch
from urllib.parse import urlparse
import hashlib

# ---------------- Query Generator ----------------
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

# ---------------- SerpAPI + Save ----------------
def search_and_save(query, borrower_id, serpapi_api_key, num_results=3):
    os.makedirs('articles', exist_ok=True)

    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_api_key,
        "num": num_results
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    links = []
    if "organic_results" in results:
        for res in results["organic_results"]:
            link = res.get("link")
            if link:
                links.append(link)

    saved_files = []
    for idx, url in enumerate(links):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.text

            url_hash = hashlib.md5(url.encode()).hexdigest()
            parsed = urlparse(url)
            domain = parsed.netloc.replace(".", "_")
            filename = f"articles/{borrower_id}_q{idx+1}_{domain}_{url_hash}.html"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            saved_files.append(filename)

        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    return saved_files
