import os
import re
import time
import pandas as pd
import requests
import json
import google.generativeai as genai
from keys import SERP_KEY, GEMINI_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_queries(job_title, company, industry, years_ahead=5):
    """Generate specific queries for loan risk assessment"""
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

def search_serpapi(query, num_results=15):
    """Search using SerpAPI Google Search"""
    articles = []
    
    try:
        # SerpAPI parameters
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERP_KEY,
            "num": num_results,
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com"
        }
        
        print(f"  Searching: {query}")
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract organic results
        organic_results = data.get("organic_results", [])
        
        for i, result in enumerate(organic_results[:num_results]):
            try:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Also check for rich snippets
                if not snippet:
                    snippet = result.get("rich_snippet", {}).get("top", {}).get("detected_extensions", {}).get("description", "")
                
                if title and link:
                    articles.append({
                        'title': title.replace('\n', ' ').strip(),
                        'link': link,
                        'snippet': snippet.replace('\n', ' ').strip() if snippet else ""
                    })
                    
            except Exception as e:
                continue
        
        # Also get news results if available
        news_results = data.get("news_results", [])
        for i, result in enumerate(news_results[:min(3, num_results - len(articles))]):
            try:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                if title and link:
                    articles.append({
                        'title': f"[NEWS] {title}".replace('\n', ' ').strip(),
                        'link': link,
                        'snippet': snippet.replace('\n', ' ').strip() if snippet else ""
                    })
                    
            except Exception as e:
                continue
        
    except requests.exceptions.RequestException as e:
        print(f"    Error making SerpAPI request: {e}")
    except json.JSONDecodeError as e:
        print(f"    Error parsing SerpAPI response: {e}")
    except Exception as e:
        print(f"    Unexpected error during SerpAPI search: {e}")
    
    return articles

def rank_articles_with_gemini(articles, query, top_k=3):
    """Use Gemini to rank articles by relevance to the query"""
    if not articles:
        return []
    
    # Prepare articles for ranking
    articles_text = ""
    for i, article in enumerate(articles):
        articles_text += f"""
Article {i+1}:
Title: {article['title']}
Snippet: {article['snippet']}
URL: {article['link']}
---
"""
    
    ranking_prompt = f"""
You are an expert content ranker. Given the search query: "{query}"

Please rank the following articles by their relevance to the query. Consider:
1. How well the title matches the query intent
2. How relevant the snippet content is
3. The credibility of the source (based on URL)
4. The freshness and specificity of the information
5. Authority of the domain (news sites, academic sources, official websites)

Articles to rank:
{articles_text}

Return only the top {top_k} article numbers (1-{len(articles)}) in order of relevance, separated by commas.
For example: 3,1,7

Your response (just the numbers):
"""
    
    try:
        response = model.generate_content(ranking_prompt)
        ranking_text = response.text.strip()
        
        # Parse the ranking
        ranked_indices = []
        for num_str in ranking_text.split(','):
            try:
                idx = int(num_str.strip()) - 1  # Convert to 0-based index
                if 0 <= idx < len(articles):
                    ranked_indices.append(idx)
            except ValueError:
                continue
        
        # Return top ranked articles
        ranked_articles = [articles[i] for i in ranked_indices[:top_k]]
        
        # If we don't have enough ranked articles, fill with remaining ones
        if len(ranked_articles) < top_k:
            used_indices = set(ranked_indices[:top_k])
            for i, article in enumerate(articles):
                if i not in used_indices and len(ranked_articles) < top_k:
                    ranked_articles.append(article)
        
        return ranked_articles
        
    except Exception as e:
        print(f"    Error ranking with Gemini: {e}")
        # Fallback: return first top_k articles
        return articles[:top_k]

def search_single_query(query, borrower_id, output_dir="clean_articles"):
    """Search for a single query and save results"""
    articles = search_serpapi(query, num_results=10)
    
    if not articles:
        print(f"    No articles found for: {query}")
        return None
    
    # Rank articles
    top_articles = rank_articles_with_gemini(articles, query, top_k=3)
    
    # Create content
    content = f"Search Query: {query}\n"
    content += f"Search Engine: Google (via SerpAPI)\n"
    content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"Borrower ID: {borrower_id}\n"
    content += "=" * 80 + "\n\n"
    
    # Add articles
    for i, article in enumerate(top_articles):
        content += f"{i+1}. {article['title']}\n"
        content += f"   URL: {article['link']}\n"
        content += f"   Summary: {article['snippet']}\n\n"
    
    # Save to file
    safe_query = re.sub(r'[^\w\s-]', '', query).replace(' ', '_')[:50]
    filename = f"{output_dir}/SERP_{borrower_id}_{safe_query}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"    Saved: {filename}")
        return filename
    except Exception as e:
        print(f"    Error saving: {e}")
        return None

def process_borrower_serp(borrower_row, output_dir="clean_articles"):
    """Process a single borrower with SerpAPI search"""
    borrower_id = borrower_row['borrower_id']
    borrower_name = borrower_row['borrower_name']
    job_title = borrower_row['job_title']
    company = borrower_row['company']
    industry = borrower_row['industry']
    
    print(f"\n=== Processing Borrower {borrower_id}: {borrower_name} ===")
    print(f"Job: {job_title} at {company} ({industry})")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate queries
    queries = generate_queries(job_title, company, industry)
    
    # Search each query
    saved_files = []
    for i, query in enumerate(queries):
        print(f"  Query {i+1}/{len(queries)}: {query[:60]}...")
        filename = search_single_query(query, borrower_id, output_dir)
        if filename:
            saved_files.append(filename)
        
        # Be polite to the API
        time.sleep(1)
    
    print(f"  Completed: {len(saved_files)}/{len(queries)} queries saved")
    return saved_files

def check_serpapi_quota():
    """Check SerpAPI quota and usage"""
    try:
        response = requests.get(f"https://serpapi.com/account?api_key={SERP_KEY}")
        if response.status_code == 200:
            data = response.json()
            print(f"SerpAPI Account Info:")
            print(f"  Plan: {data.get('plan', 'Unknown')}")
            print(f"  Searches this month: {data.get('total_searches_this_month', 0)}")
            print(f"  Searches left: {data.get('searches_left_this_month', 0)}")
            return True
    except Exception as e:
        print(f"Could not check SerpAPI quota: {e}")
        return False

def process_borrowers_from_csv(csv_file, output_dir="clean_articles"):
    """Process all borrowers from CSV file"""
    try:
        # Read CSV
        df = pd.read_csv(csv_file)
        
        print(f"SerpAPI Borrower Article Searcher")
        print("=" * 60)
        print(f"Found {len(df)} borrowers to process")
        print(f"Output directory: {output_dir}")
        
        # Check quota
        print("\nChecking SerpAPI quota...")
        quota_ok = check_serpapi_quota()
        if not quota_ok:
            print("Warning: Could not verify SerpAPI quota")
        
        # Process each borrower
        total_files = 0
        for index, row in df.iterrows():
            try:
                files = process_borrower_serp(row, output_dir)
                total_files += len(files)
                
                # Pause between borrowers
                if index < len(df) - 1:
                    print(f"  Pausing before next borrower...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"  Error processing borrower {row.get('borrower_id', 'unknown')}: {e}")
                continue
        
        print(f"\n=== Processing Complete ===")
        print(f"Total files saved: {total_files}")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def main():
    """Main function"""
    print("SerpAPI Borrower Risk Assessment Searcher")
    print("=" * 60)
    
    # Check if loan_data.csv exists
    csv_file = "loan_data.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please ensure the CSV file with borrower data exists.")
        return
    
    # Ask user for confirmation
    try:
        df = pd.read_csv(csv_file)
        print(f"Found {len(df)} borrowers in {csv_file}")
        print(f"Each borrower will generate 12 searches")
        print(f"Total searches: {len(df) * 12}")
        
        proceed = input("\nProceed with searches? (y/n): ").lower().strip()
        if proceed != 'y':
            print("Cancelled.")
            return
        
        # Process borrowers
        process_borrowers_from_csv(csv_file)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
