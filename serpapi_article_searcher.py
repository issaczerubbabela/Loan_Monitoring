import os
import re
import time
import requests
import json
import google.generativeai as genai
from keys import SERP_KEY, GEMINI_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def search_serpapi(query, num_results=10):
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
        
        print(f"Searching SerpAPI for: {query}")
        
        # Make API request
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract organic results
        organic_results = data.get("organic_results", [])
        
        print(f"Found {len(organic_results)} SerpAPI results")
        
        for i, result in enumerate(organic_results[:num_results]):
            try:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Also check for rich snippets or additional content
                if not snippet:
                    snippet = result.get("rich_snippet", {}).get("top", {}).get("detected_extensions", {}).get("description", "")
                
                if title and link:
                    articles.append({
                        'title': title.replace('\n', ' ').strip(),
                        'link': link,
                        'snippet': snippet.replace('\n', ' ').strip() if snippet else ""
                    })
                    print(f"SerpAPI article {i+1}: {title[:50]}...")
                    
            except Exception as e:
                print(f"Error extracting SerpAPI result {i+1}: {e}")
                continue
        
        # Also try to get news results if available
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
                    print(f"SerpAPI news article {i+1}: {title[:50]}...")
                    
            except Exception as e:
                print(f"Error extracting SerpAPI news result {i+1}: {e}")
                continue
        
    except requests.exceptions.RequestException as e:
        print(f"Error making SerpAPI request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing SerpAPI response: {e}")
    except Exception as e:
        print(f"Unexpected error during SerpAPI search: {e}")
    
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
7. Provide actionable insights and conclusions

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
    """Main function to search, rank, and save articles using SerpAPI"""
    print(f"\n=== Searching for: {query} ===")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Search for articles using SerpAPI
    articles = search_serpapi(query, num_results=15)
    
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
    filename = f"{output_dir}/SERP_{safe_query}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Search Query: {query}\n")
            f.write(f"Search Engine: Google (via SerpAPI)\n")
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

def main():
    """Example usage"""
    sample_queries = [
        "artificial intelligence job market 2025",
        "electric vehicle adoption trends 2024",
        "remote work future predictions",
        "cryptocurrency regulation updates 2024",
        "climate change impact on agriculture"
    ]
    
    print("SerpAPI Article Searcher")
    print("=" * 50)
    
    # Check API quota
    check_serpapi_quota()
    print()
    
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
            
            # Be polite to the API
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            continue
    
    print("\n=== All searches completed ===")

if __name__ == "__main__":
    main()
