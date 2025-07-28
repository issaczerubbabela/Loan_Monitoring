import pandas as pd
import requests
import json
from google.generativeai import configure, GenerativeModel
from playwright.sync_api import sync_playwright
from urllib.parse import quote
import time
import re
from keys import GEMINI_KEY

# --------------------- Gemini API Setup ---------------------
configure(api_key=GEMINI_KEY)
gemini = GenerativeModel("gemini-2.5-flash")

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

# Web scraping with Playwright
def scrape_search_results(query, num_results=10):
    """Scrape search results from Google using Playwright with multiple fallback strategies"""
    articles = []
    
    with sync_playwright() as p:
        try:
            # Launch browser in headless mode with additional options
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            page = browser.new_page()
            
            # Set user agent and additional headers to avoid bot detection
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            })
            
            # Remove webdriver property
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Perform Google search
            search_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}&hl=en"
            print(f"Navigating to: {search_url}")
            
            page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            # Wait for results to load
            page.wait_for_timeout(3000)
            
            # Debug: Check if we can see the page content
            page_title = page.title()
            print(f"Page title: {page_title}")
            
            # Multiple selector strategies for different Google layouts
            selectors_to_try = [
                'div.g',           # Classic Google result container
                'div[data-ved]',   # Alternative container
                '.tF2Cxc',         # Another common container
                '.g',              # Simple class
                '[data-sokoban-container]'  # Newer Google layout
            ]
            
            result_elements = []
            for selector in selectors_to_try:
                result_elements = page.query_selector_all(selector)
                if result_elements:
                    print(f"Found {len(result_elements)} results using selector: {selector}")
                    break
            
            if not result_elements:
                print("No result elements found with any selector")
                # Take a screenshot for debugging
                page.screenshot(path="debug_google_search.png")
                browser.close()
                return articles
            
            for i, element in enumerate(result_elements[:num_results]):
                try:
                    # Multiple strategies for extracting title
                    title = ""
                    title_selectors = ['h3', 'h3 a', '[role="heading"]', '.LC20lb']
                    for title_sel in title_selectors:
                        title_elem = element.query_selector(title_sel)
                        if title_elem:
                            title = title_elem.inner_text().strip()
                            break
                    
                    # Multiple strategies for extracting link
                    link = ""
                    link_selectors = ['a[href]', 'h3 a', 'a']
                    for link_sel in link_selectors:
                        link_elem = element.query_selector(link_sel)
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href and href.startswith('http'):
                                link = href
                                break
                    
                    # Multiple strategies for extracting snippet
                    snippet = ""
                    snippet_selectors = [
                        '.VwiC3b', 
                        '.s3v9rd', 
                        '.st', 
                        '[data-sncf]', 
                        '.IsZvec',
                        'span[data-ved]'
                    ]
                    for snippet_sel in snippet_selectors:
                        snippet_elem = element.query_selector(snippet_sel)
                        if snippet_elem:
                            snippet = snippet_elem.inner_text().strip()
                            break
                    
                    if title and link:
                        article = {
                            'title': title.replace('\n', ' ').strip(),
                            'link': link,
                            'snippet': snippet.replace('\n', ' ').strip() if snippet else ""
                        }
                        articles.append(article)
                        print(f"Extracted article {i+1}: {title[:50]}...")
                    else:
                        print(f"Skipping result {i+1}: title='{title[:30]}', link='{link[:30]}'")
                        
                except Exception as e:
                    print(f"Error extracting individual result {i+1}: {e}")
                    continue
            
            browser.close()
            
        except Exception as e:
            print(f"Error during web scraping: {e}")
            # Try to close browser if it's still open
            try:
                browser.close()
            except:
                pass
            
    print(f"Total articles extracted: {len(articles)}")
    return articles

def scrape_duckduckgo_results(query, num_results=10):
    """Fallback search using DuckDuckGo (more scraping-friendly)"""
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
            print(f"Trying DuckDuckGo: {search_url}")
            
            page.goto(search_url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            # DuckDuckGo result selectors
            result_elements = page.query_selector_all('[data-testid="result"]')
            
            if not result_elements:
                # Try alternative selector
                result_elements = page.query_selector_all('.nrn-react-div')
            
            print(f"Found {len(result_elements)} DuckDuckGo results")
            
            for i, element in enumerate(result_elements[:num_results]):
                try:
                    # Extract title
                    title_elem = element.query_selector('h2 a') or element.query_selector('a[data-testid="result-title-a"]')
                    title = title_elem.inner_text().strip() if title_elem else ""
                    
                    # Extract link
                    link_elem = element.query_selector('h2 a') or element.query_selector('a[data-testid="result-title-a"]')
                    link = link_elem.get_attribute('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = element.query_selector('[data-testid="result-snippet"]') or element.query_selector('.E2eLOJr8HctVnDOTM8fs')
                    snippet = snippet_elem.inner_text().strip() if snippet_elem else ""
                    
                    if title and link:
                        articles.append({
                            'title': title.replace('\n', ' ').strip(),
                            'link': link,
                            'snippet': snippet.replace('\n', ' ').strip()
                        })
                        print(f"DuckDuckGo article {i+1}: {title[:50]}...")
                        
                except Exception as e:
                    print(f"Error extracting DuckDuckGo result {i+1}: {e}")
                    continue
            
            browser.close()
            
        except Exception as e:
            print(f"Error during DuckDuckGo scraping: {e}")
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

Articles to rank:
{articles_text}

Return only the top {top_k} article numbers (1-{len(articles)}) in order of relevance, separated by commas.
For example: 3,1,7

Your response (just the numbers):
"""
    
    try:
        response = gemini.generate_content(ranking_prompt)
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
        print(f"Error ranking articles with Gemini: {e}")
        # Fallback: return first top_k articles
        return articles[:top_k]

def search_web(query, borrower_id=None, num_results=3):
    """Main search function using Playwright + Gemini ranking with fallback options"""
    print(f"Searching for: {query}")
    
    # Try Google first
    scraped_articles = scrape_search_results(query, num_results * 3)
    
    # If Google fails, try DuckDuckGo
    if not scraped_articles:
        print("Google search failed, trying DuckDuckGo...")
        scraped_articles = scrape_duckduckgo_results(query, num_results * 3)
    
    # If both fail, return a simple message
    if not scraped_articles:
        print(f"No articles found for query: {query}")
        # Create a minimal fallback response
        fallback_response = f"Search query: {query}\nNo articles found through web scraping.\nThis may be due to network issues or changes in search engine structure."
        
        # Save the fallback response
        safe_query = re.sub(r'[^\w\s-]', '', query).replace(' ', '_')[:50]
        filename = f"articles/{borrower_id}_{safe_query}.txt" if borrower_id else f"articles/{safe_query}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(fallback_response)
        except Exception as e:
            print(f"Error saving fallback response: {e}")
        
        return fallback_response
    
    print(f"Found {len(scraped_articles)} articles, ranking with Gemini...")
    
    # Rank articles using Gemini and get top results
    top_articles = rank_articles_with_gemini(scraped_articles, query, num_results)
    
    # Format articles for output
    formatted_articles = []
    for article in top_articles:
        formatted_articles.append(f"{article['title']}\n{article['snippet']}\n{article['link']}")
    
    # Save articles to file
    safe_query = re.sub(r'[^\w\s-]', '', query).replace(' ', '_')[:50]
    filename = f"articles/{borrower_id}_{safe_query}.txt" if borrower_id else f"articles/{safe_query}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n\n".join(formatted_articles))
        print(f"Saved {len(formatted_articles)} articles to {filename}")
    except Exception as e:
        print(f"Error saving articles to file: {e}")
    
    # Be polite to the web servers
    time.sleep(2)
    
    return "\n\n".join(formatted_articles)

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
