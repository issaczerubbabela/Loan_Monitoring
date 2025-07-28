import os
import re
import time
import pandas as pd
from urllib.parse import quote
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from keys import GEMINI_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

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

def scrape_duckduckgo_results(query, num_results=10):
    """Scrape search results from DuckDuckGo using Playwright"""
    articles = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Set user agent
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # DuckDuckGo search
            search_url = f"https://duckduckgo.com/?q={quote(query)}"
            print(f"  Searching: {query}")
            
            page.goto(search_url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            
            # DuckDuckGo result selectors
            result_elements = page.query_selector_all('[data-testid="result"]')
            
            if not result_elements:
                result_elements = page.query_selector_all('.nrn-react-div')
            
            if not result_elements:
                result_elements = page.query_selector_all('[data-layout="organic"]')
            
            for i, element in enumerate(result_elements[:num_results]):
                try:
                    # Extract title
                    title_elem = (element.query_selector('h2 a') or 
                                 element.query_selector('a[data-testid="result-title-a"]') or
                                 element.query_selector('h3 a'))
                    title = title_elem.inner_text().strip() if title_elem else ""
                    
                    # Extract link
                    link_elem = (element.query_selector('h2 a') or 
                                element.query_selector('a[data-testid="result-title-a"]') or
                                element.query_selector('h3 a'))
                    link = link_elem.get_attribute('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = (element.query_selector('[data-testid="result-snippet"]') or 
                                   element.query_selector('.E2eLOJr8HctVnDOTM8fs') or
                                   element.query_selector('.snippet'))
                    snippet = snippet_elem.inner_text().strip() if snippet_elem else ""
                    
                    if title and link:
                        articles.append({
                            'title': title.replace('\n', ' ').strip(),
                            'link': link,
                            'snippet': snippet.replace('\n', ' ').strip()
                        })
                        
                except Exception as e:
                    continue
            
            browser.close()
            
        except Exception as e:
            print(f"    Error during scraping: {e}")
            try:
                browser.close()
            except:
                pass
    
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
    articles = scrape_duckduckgo_results(query, num_results=10)
    
    if not articles:
        print(f"    No articles found for: {query}")
        return None
    
    # Rank articles
    top_articles = rank_articles_with_gemini(articles, query, top_k=3)
    
    # Create content
    content = f"Search Query: {query}\n"
    content += f"Search Engine: DuckDuckGo\n"
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
    filename = f"{output_dir}/DDG_{borrower_id}_{safe_query}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"    Saved: {filename}")
        return filename
    except Exception as e:
        print(f"    Error saving: {e}")
        return None

def process_borrower_ddg(borrower_row, output_dir="clean_articles"):
    """Process a single borrower with DuckDuckGo search"""
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
        
        # Be polite to servers
        time.sleep(1)
    
    print(f"  Completed: {len(saved_files)}/{len(queries)} queries saved")
    return saved_files

def process_borrowers_from_csv(csv_file, output_dir="clean_articles"):
    """Process all borrowers from CSV file"""
    try:
        # Read CSV
        df = pd.read_csv(csv_file)
        
        print(f"DuckDuckGo Borrower Article Searcher")
        print("=" * 60)
        print(f"Found {len(df)} borrowers to process")
        print(f"Output directory: {output_dir}")
        
        # Process each borrower
        total_files = 0
        for index, row in df.iterrows():
            try:
                files = process_borrower_ddg(row, output_dir)
                total_files += len(files)
                
                # Pause between borrowers
                if index < len(df) - 1:
                    print(f"  Pausing before next borrower...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"  Error processing borrower {row.get('borrower_id', 'unknown')}: {e}")
                continue
        
        print(f"\n=== Processing Complete ===")
        print(f"Total files saved: {total_files}")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def main():
    """Main function"""
    print("DuckDuckGo Borrower Risk Assessment Searcher")
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
