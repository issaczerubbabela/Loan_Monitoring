import os
import re
import time
import json
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from keys import GEMINI_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def extract_urls_from_article_files(articles_dir="clean_articles"):
    """Extract all URLs from article files"""
    urls_data = []
    
    if not os.path.exists(articles_dir):
        print(f"Directory {articles_dir} does not exist")
        return urls_data
    
    files = [f for f in os.listdir(articles_dir) if f.endswith('.txt')]
    print(f"Found {len(files)} article files to process")
    
    for filename in files:
        filepath = os.path.join(articles_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract borrower ID and query info
            borrower_id = None
            search_query = None
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Search Query:'):
                    search_query = line.replace('Search Query:', '').strip()
                elif line.startswith('Borrower ID:'):
                    borrower_id = line.replace('Borrower ID:', '').strip()
                elif line.startswith('==='):
                    break
            
            # Extract URLs
            url_pattern = r'URL: (https?://[^\s\n]+)'
            urls = re.findall(url_pattern, content)
            
            for url in urls:
                urls_data.append({
                    'url': url.strip(),
                    'borrower_id': borrower_id,
                    'search_query': search_query,
                    'source_file': filename
                })
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"Extracted {len(urls_data)} URLs from article files")
    return urls_data

def scrape_web_content(url, max_retries=3):
    """Scrape full content from a webpage"""
    
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent and headers
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                })
                
                # Navigate to page
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                
                # Get page title
                title = page.title()
                
                # Extract main content using multiple strategies
                content = ""
                
                # Strategy 1: Try to find main content areas
                content_selectors = [
                    'main',
                    'article', 
                    '.content',
                    '.main-content',
                    '.article-content',
                    '.post-content',
                    '.entry-content',
                    '.story-body',
                    '.article-body',
                    '#content',
                    '#main-content'
                ]
                
                for selector in content_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            content = element.inner_text()
                            if len(content) > 500:  # Good content length
                                break
                    except:
                        continue
                
                # Strategy 2: If no main content found, get body text
                if not content or len(content) < 500:
                    try:
                        # Remove scripts, styles, and navigation
                        page.evaluate("""
                            // Remove unwanted elements
                            const unwanted = document.querySelectorAll('script, style, nav, header, footer, aside, .nav, .navigation, .menu, .sidebar, .ads, .advertisement');
                            unwanted.forEach(el => el.remove());
                        """)
                        
                        body_element = page.query_selector('body')
                        if body_element:
                            content = body_element.inner_text()
                    except:
                        content = ""
                
                # Strategy 3: Get all paragraph text
                if not content or len(content) < 200:
                    try:
                        paragraphs = page.query_selector_all('p')
                        paragraph_texts = []
                        for p in paragraphs:
                            text = p.inner_text().strip()
                            if len(text) > 50:  # Skip very short paragraphs
                                paragraph_texts.append(text)
                        content = '\n\n'.join(paragraph_texts)
                    except:
                        content = ""
                
                browser.close()
                
                # Clean up content
                content = content.strip()
                
                # Remove excessive whitespace
                content = re.sub(r'\n\s*\n', '\n\n', content)
                content = re.sub(r' +', ' ', content)
                
                if len(content) < 100:
                    print(f"  Warning: Very short content ({len(content)} chars) for {url}")
                
                return {
                    'url': url,
                    'title': title,
                    'content': content,
                    'content_length': len(content),
                    'status': 'success'
                }
                
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            continue
    
    return {
        'url': url,
        'title': '',
        'content': '',
        'content_length': 0,
        'status': 'failed',
        'error': f'Failed after {max_retries} attempts'
    }

def clean_and_summarize_content(content, url, search_query):
    """Use Gemini to clean and summarize the scraped content"""
    if not content or len(content) < 100:
        return content
    
    # If content is very long, truncate it for Gemini
    if len(content) > 10000:
        content = content[:10000] + "...\n[Content truncated for processing]"
    
    prompt = f"""
Please clean and summarize the following web content. The content was scraped from {url} for the search query: "{search_query}"

Requirements:
1. Remove any navigation text, ads, cookie notices, or irrelevant content
2. Focus on the main article content
3. Summarize key points while maintaining important details
4. Organize information with clear headers if appropriate
5. Keep the summary comprehensive but concise (aim for 300-800 words)
6. Maintain factual accuracy and important numbers/statistics

Web Content:
{content}

Please provide a clean, well-organized summary:
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  Error summarizing content with Gemini: {e}")
        # Return original content if Gemini fails
        return content

def save_web_content(url_data, web_content, output_dir="web_content"):
    """Save scraped web content to file"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create safe filename
    domain = urlparse(url_data['url']).netloc
    safe_domain = re.sub(r'[^\w\.-]', '_', domain)
    safe_query = re.sub(r'[^\w\s-]', '', url_data['search_query'] or 'unknown')
    safe_query = safe_query.replace(' ', '_')[:50]
    
    filename = f"{url_data['borrower_id']}_{safe_domain}_{safe_query}.txt"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url_data['url']}\n")
            f.write(f"Borrower ID: {url_data['borrower_id']}\n")
            f.write(f"Search Query: {url_data['search_query']}\n")
            f.write(f"Source File: {url_data['source_file']}\n")
            f.write(f"Page Title: {web_content['title']}\n")
            f.write(f"Content Length: {web_content['content_length']} characters\n")
            f.write(f"Scraping Status: {web_content['status']}\n")
            f.write(f"Date Scraped: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if web_content['status'] == 'success':
                f.write(web_content['content'])
            else:
                f.write(f"Error: {web_content.get('error', 'Unknown error')}")
        
        return filepath
    except Exception as e:
        print(f"  Error saving content to {filepath}: {e}")
        return None

def scrape_all_urls(articles_dir="clean_articles", output_dir="web_content", use_gemini_summary=True):
    """Main function to scrape all URLs from article files"""
    
    print("=" * 80)
    print("WEB CONTENT SCRAPER")
    print("=" * 80)
    
    # Extract URLs from article files
    urls_data = extract_urls_from_article_files(articles_dir)
    
    if not urls_data:
        print("No URLs found to scrape")
        return
    
    # Remove duplicates
    unique_urls = {}
    for url_data in urls_data:
        if url_data['url'] not in unique_urls:
            unique_urls[url_data['url']] = url_data
    
    print(f"Found {len(unique_urls)} unique URLs to scrape")
    
    # Ask for confirmation
    proceed = input(f"\nProceed with scraping {len(unique_urls)} URLs? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Cancelled.")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Scrape each URL
    successful = 0
    failed = 0
    
    for i, (url, url_data) in enumerate(unique_urls.items(), 1):
        print(f"\n[{i}/{len(unique_urls)}] Scraping: {url}")
        
        # Scrape content
        web_content = scrape_web_content(url)
        
        if web_content['status'] == 'success':
            # Optionally clean and summarize with Gemini
            if use_gemini_summary and web_content['content']:
                print(f"  Cleaning content with Gemini...")
                cleaned_content = clean_and_summarize_content(
                    web_content['content'], 
                    url, 
                    url_data['search_query']
                )
                web_content['content'] = cleaned_content
            
            # Save content
            filepath = save_web_content(url_data, web_content, output_dir)
            if filepath:
                print(f"  ✓ Saved to: {os.path.basename(filepath)}")
                successful += 1
            else:
                print(f"  ✗ Failed to save")
                failed += 1
        else:
            print(f"  ✗ Failed to scrape: {web_content.get('error', 'Unknown error')}")
            failed += 1
        
        # Be polite to servers
        time.sleep(2)
    
    print(f"\n" + "=" * 80)
    print(f"SCRAPING COMPLETED")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)

def main():
    """Main function with options"""
    print("Web Content Scraper for Borrower Articles")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Scrape all URLs (with Gemini summary)
2. Scrape all URLs (without Gemini summary) 
3. Show URLs that would be scraped
4. Exit

Enter choice (1-4): """).strip()
    
    if choice == "1":
        scrape_all_urls(use_gemini_summary=True)
    elif choice == "2":
        scrape_all_urls(use_gemini_summary=False)
    elif choice == "3":
        urls_data = extract_urls_from_article_files()
        unique_urls = list(set(url_data['url'] for url_data in urls_data))
        print(f"\nFound {len(unique_urls)} unique URLs:")
        for i, url in enumerate(unique_urls, 1):
            print(f"{i:3d}. {url}")
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
