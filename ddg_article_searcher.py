import os
import re
import time
from urllib.parse import quote
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from keys import GEMINI_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

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
            print(f"Searching DuckDuckGo: {search_url}")
            
            page.goto(search_url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            # DuckDuckGo result selectors
            result_elements = page.query_selector_all('[data-testid="result"]')
            
            if not result_elements:
                # Try alternative selectors
                result_elements = page.query_selector_all('.nrn-react-div')
            
            if not result_elements:
                result_elements = page.query_selector_all('[data-layout="organic"]')
            
            print(f"Found {len(result_elements)} DuckDuckGo results")
            
            for i, element in enumerate(result_elements[:num_results]):
                try:
                    # Extract title
                    title_elem = (element.query_selector('h2 a') or 
                                 element.query_selector('a[data-testid="result-title-a"]') or
                                 element.query_selector('h3 a') or
                                 element.query_selector('a[data-layout="organic"]'))
                    title = title_elem.inner_text().strip() if title_elem else ""
                    
                    # Extract link
                    link_elem = (element.query_selector('h2 a') or 
                                element.query_selector('a[data-testid="result-title-a"]') or
                                element.query_selector('h3 a') or
                                element.query_selector('a[data-layout="organic"]'))
                    link = link_elem.get_attribute('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = (element.query_selector('[data-testid="result-snippet"]') or 
                                   element.query_selector('.E2eLOJr8HctVnDOTM8fs') or
                                   element.query_selector('[data-result="snippet"]') or
                                   element.query_selector('.snippet'))
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

def rank_articles_with_gemini(articles, query, top_k=5):
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
        print(f"Error ranking articles with Gemini: {e}")
        # Fallback: return first top_k articles
        return articles[:top_k]

def create_clean_article_summary(articles, query):
    """Use Gemini to create a clean, comprehensive summary of the articles"""
    if not articles:
        return f"No articles found for query: {query}"
    
    articles_content = ""
    for i, article in enumerate(articles):
        articles_content += f"""
Article {i+1}: {article['title']}
Source: {article['link']}
Content: {article['snippet']}

---
"""
    
    summary_prompt = f"""
Based on the following articles about "{query}", create a comprehensive, well-structured summary that combines the key insights from all sources.

Requirements:
1. Write in clear, professional prose
2. Organize information logically with headers
3. Include key facts, trends, and insights
4. Mention important sources when relevant
5. Avoid redundancy while being comprehensive
6. Use proper formatting with headers and bullet points where appropriate

Articles:
{articles_content}

Create a clean, informative summary:
"""
    
    try:
        response = model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error creating summary with Gemini: {e}")
        # Fallback: return formatted articles
        fallback = f"Search Results for: {query}\n\n"
        for i, article in enumerate(articles):
            fallback += f"{i+1}. {article['title']}\n"
            fallback += f"   Source: {article['link']}\n"
            fallback += f"   Summary: {article['snippet']}\n\n"
        return fallback

def search_and_save_articles(query, output_dir="clean_articles", top_k=5):
    """Main function to search, rank, and save articles"""
    print(f"\n=== Searching for: {query} ===")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Search for articles
    articles = scrape_duckduckgo_results(query, num_results=15)
    
    if not articles:
        print(f"No articles found for query: {query}")
        return None
    
    print(f"Found {len(articles)} articles, ranking with Gemini...")
    
    # Rank articles using Gemini
    top_articles = rank_articles_with_gemini(articles, query, top_k)
    
    # Create clean summary
    clean_summary = create_clean_article_summary(top_articles, query)
    
    # Save to file
    safe_query = re.sub(r'[^\w\s-]', '', query).replace(' ', '_')[:50]
    filename = f"{output_dir}/DDG_{safe_query}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Search Query: {query}\n")
            f.write(f"Search Engine: DuckDuckGo\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Top {len(top_articles)} articles selected and summarized\n")
            f.write("=" * 80 + "\n\n")
            f.write(clean_summary)
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("SOURCE ARTICLES:\n\n")
            
            for i, article in enumerate(top_articles):
                f.write(f"{i+1}. {article['title']}\n")
                f.write(f"   URL: {article['link']}\n")
                f.write(f"   Snippet: {article['snippet']}\n\n")
        
        print(f"Saved clean article summary to: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error saving article summary: {e}")
        return None

def main():
    """Example usage"""
    sample_queries = [
        "artificial intelligence job market 2025",
        "electric vehicle adoption trends 2024",
        "remote work future predictions",
        "cryptocurrency regulation updates 2024",
        "climate change impact on agriculture"
    ]
    
    print("DuckDuckGo Article Searcher")
    print("=" * 50)
    
    # You can either use sample queries or input your own
    use_samples = input("Use sample queries? (y/n): ").lower().strip() == 'y'
    
    if use_samples:
        queries = sample_queries
    else:
        queries = []
        while True:
            query = input("Enter search query (or 'quit' to finish): ").strip()
            if query.lower() == 'quit':
                break
            if query:
                queries.append(query)
    
    # Process each query
    for query in queries:
        try:
            result_file = search_and_save_articles(query)
            if result_file:
                print(f"✓ Completed: {query}")
            else:
                print(f"✗ Failed: {query}")
            
            # Be polite to the servers
            time.sleep(3)
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            continue
    
    print("\n=== All searches completed ===")

if __name__ == "__main__":
    main()
