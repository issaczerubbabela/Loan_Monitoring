import os
import re
import time
import json
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from keys import GEMINI_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def extract_urls_from_files(articles_dir="clean_articles"):
    """Extract all URLs from article files with metadata"""
    urls_data = []
    
    if not os.path.exists(articles_dir):
        print(f"Directory {articles_dir} does not exist")
        return urls_data
    
    files = [f for f in os.listdir(articles_dir) if f.endswith('.txt')]
    
    for filename in files:
        filepath = os.path.join(articles_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            borrower_id = None
            search_query = None
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Search Query:'):
                    search_query = line.replace('Search Query:', '').strip()
                elif line.startswith('Borrower ID:'):
                    borrower_id = line.replace('Borrower ID:', '').strip()
            
            # Extract URLs with their context
            url_pattern = r'(\d+)\.\s*([^\n]+)\n\s*URL: (https?://[^\s\n]+)\n\s*Summary: ([^\n]+)'
            matches = re.findall(url_pattern, content)
            
            for match in matches:
                article_num, title, url, summary = match
                urls_data.append({
                    'url': url.strip(),
                    'title': title.strip(),
                    'summary': summary.strip(),
                    'borrower_id': borrower_id,
                    'search_query': search_query,
                    'source_file': filename,
                    'article_number': article_num
                })
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    return urls_data

def scrape_website_content(url, timeout=30000):
    """Scrape content from a single website"""
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            page = browser.new_page()
            
            # Set realistic headers
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            })
            
            # Navigate to page
            page.goto(url, wait_until="networkidle", timeout=timeout)
            page.wait_for_timeout(3000)
            
            # Get basic page info
            title = page.title()
            
            # Remove unwanted elements
            page.evaluate("""
                // Remove scripts, styles, ads, navigation
                const unwanted = document.querySelectorAll(`
                    script, style, nav, header, footer, aside, 
                    .nav, .navigation, .menu, .sidebar, .ads, .advertisement,
                    .social-share, .comments, .related-posts, .popup, .modal,
                    [class*="ad"], [class*="banner"], [class*="popup"], [class*="modal"]
                `);
                unwanted.forEach(el => el.remove());
                
                // Remove elements with minimal text
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    const text = el.innerText || el.textContent || '';
                    if (text.length < 10 && !['img', 'br', 'hr'].includes(el.tagName.toLowerCase())) {
                        if (el.children.length === 0) {
                            el.remove();
                        }
                    }
                });
            """)
            
            # Extract content using multiple strategies
            content = ""
            
            # Strategy 1: Look for main content containers
            main_selectors = [
                'main article',
                'main',
                'article',
                '.main-content',
                '.content',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.story-body',
                '.article-body',
                '#main-content',
                '#content'
            ]
            
            for selector in main_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            text = element.inner_text().strip()
                            if len(text) > 300:  # Substantial content
                                content += text + "\n\n"
                        if content:
                            break
                except:
                    continue
            
            # Strategy 2: Get all meaningful paragraphs
            if len(content) < 300:
                try:
                    paragraphs = page.query_selector_all('p')
                    paragraph_texts = []
                    
                    for p in paragraphs:
                        text = p.inner_text().strip()
                        # Filter out navigation, ads, etc.
                        if (len(text) > 50 and 
                            not any(word in text.lower() for word in ['cookie', 'privacy', 'subscribe', 'newsletter', 'advertisement'])):
                            paragraph_texts.append(text)
                    
                    if paragraph_texts:
                        content = '\n\n'.join(paragraph_texts)
                except:
                    pass
            
            # Strategy 3: Get text from specific content divs
            if len(content) < 300:
                try:
                    content_divs = page.query_selector_all('div')
                    for div in content_divs:
                        text = div.inner_text().strip()
                        if len(text) > 500:  # Substantial content
                            content = text
                            break
                except:
                    pass
            
            browser.close()
            
            # Clean up the content
            content = content.strip()
            
            # Remove excessive whitespace
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            content = re.sub(r' +', ' ', content)
            
            # Remove very short lines that are likely navigation
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if len(line) > 20 or not line:  # Keep substantial lines or empty lines
                    cleaned_lines.append(line)
            
            content = '\n'.join(cleaned_lines)
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'content_length': len(content),
                'status': 'success' if len(content) > 100 else 'low_content',
                'error': None
            }
            
    except Exception as e:
        return {
            'url': url,
            'title': '',
            'content': '',
            'content_length': 0,
            'status': 'failed',
            'error': str(e)
        }

def create_comprehensive_summary(url_data, web_content):
    """Create a comprehensive summary using Gemini"""
    
    if web_content['status'] != 'success' or len(web_content['content']) < 100:
        return web_content['content']
    
    prompt = f"""
Based on the following web content, create a comprehensive summary focused on the search query: "{url_data['search_query']}"

The original article title was: "{url_data['title']}"
The article summary was: "{url_data['summary']}"

Please analyze the full content and provide:
1. A comprehensive summary (300-500 words)
2. Key facts and statistics relevant to the search query
3. Important trends or predictions mentioned
4. Any specific company or industry insights
5. Financial data or forecasts if available

Focus on information that would be useful for loan risk assessment.

Web Content:
{web_content['content'][:8000]}{"..." if len(web_content['content']) > 8000 else ""}

Please provide a detailed, well-structured summary:
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  Error creating summary with Gemini: {e}")
        return web_content['content']

def save_scraped_content(url_data, web_content, summary, output_dir="web_content"):
    """Save scraped content to organized files"""
    
    # Create borrower-specific subdirectory
    borrower_dir = os.path.join(output_dir, f"borrower_{url_data['borrower_id']}")
    os.makedirs(borrower_dir, exist_ok=True)
    
    # Create safe filename
    domain = urlparse(url_data['url']).netloc
    safe_domain = re.sub(r'[^\w\.-]', '_', domain)
    safe_title = re.sub(r'[^\w\s-]', '', url_data['title'])
    safe_title = safe_title.replace(' ', '_')[:50]
    
    filename = f"{safe_domain}_{safe_title}.txt"
    filepath = os.path.join(borrower_dir, filename)
    
    # Ensure unique filename
    counter = 1
    original_filepath = filepath
    while os.path.exists(filepath):
        name, ext = os.path.splitext(original_filepath)
        filepath = f"{name}_{counter}{ext}"
        counter += 1
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url_data['url']}\n")
            f.write(f"Borrower ID: {url_data['borrower_id']}\n")
            f.write(f"Search Query: {url_data['search_query']}\n")
            f.write(f"Original Title: {url_data['title']}\n")
            f.write(f"Original Summary: {url_data['summary']}\n")
            f.write(f"Page Title: {web_content['title']}\n")
            f.write(f"Content Length: {web_content['content_length']} characters\n")
            f.write(f"Scraping Status: {web_content['status']}\n")
            f.write(f"Date Scraped: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if web_content['status'] == 'success':
                f.write("GEMINI SUMMARY:\n")
                f.write("-" * 40 + "\n")
                f.write(summary + "\n\n")
                f.write("FULL CONTENT:\n")
                f.write("-" * 40 + "\n")
                f.write(web_content['content'])
            else:
                f.write(f"Error: {web_content.get('error', 'Content scraping failed')}\n")
                f.write(f"Original Summary: {url_data['summary']}")
        
        return filepath
        
    except Exception as e:
        print(f"  Error saving to {filepath}: {e}")
        return None

def process_all_urls(articles_dir="clean_articles", output_dir="web_content"):
    """Process all URLs from article files"""
    
    print("=" * 80)
    print("COMPREHENSIVE WEB CONTENT SCRAPER")
    print("=" * 80)
    
    # Extract URLs
    urls_data = extract_urls_from_files(articles_dir)
    
    if not urls_data:
        print("No URLs found to process")
        return
    
    print(f"Found {len(urls_data)} URLs to scrape")
    
    # Group by borrower for better organization
    borrower_groups = {}
    for url_data in urls_data:
        borrower_id = url_data['borrower_id']
        if borrower_id not in borrower_groups:
            borrower_groups[borrower_id] = []
        borrower_groups[borrower_id].append(url_data)
    
    print(f"URLs grouped by {len(borrower_groups)} borrowers")
    
    # Confirm processing
    proceed = input(f"\nProceed with scraping? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Cancelled.")
        return
    
    # Process each borrower's URLs
    total_processed = 0
    total_successful = 0
    
    for borrower_id, urls in borrower_groups.items():
        print(f"\n{'='*50}")
        print(f"PROCESSING BORROWER {borrower_id}")
        print(f"{'='*50}")
        print(f"URLs to process: {len(urls)}")
        
        for i, url_data in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url_data['url']}")
            print(f"  Query: {url_data['search_query']}")
            
            # Scrape content
            web_content = scrape_website_content(url_data['url'])
            
            if web_content['status'] == 'success':
                print(f"  ✓ Scraped {web_content['content_length']} characters")
                
                # Create summary with Gemini
                print(f"  Creating summary with Gemini...")
                summary = create_comprehensive_summary(url_data, web_content)
                
                # Save content
                filepath = save_scraped_content(url_data, web_content, summary, output_dir)
                if filepath:
                    print(f"  ✓ Saved to: {os.path.relpath(filepath)}")
                    total_successful += 1
                else:
                    print(f"  ✗ Failed to save")
                
            else:
                print(f"  ✗ Failed: {web_content.get('error', 'Unknown error')}")
                
                # Save failed attempt info
                filepath = save_scraped_content(url_data, web_content, "", output_dir)
                if filepath:
                    print(f"  ✓ Saved error info to: {os.path.relpath(filepath)}")
            
            total_processed += 1
            
            # Be respectful to servers
            time.sleep(2)
    
    print(f"\n" + "=" * 80)
    print(f"PROCESSING COMPLETED")
    print(f"Total URLs processed: {total_processed}")
    print(f"Successfully scraped: {total_successful}")
    print(f"Failed: {total_processed - total_successful}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)

def main():
    """Main function"""
    print("Web Content Scraper for Borrower Risk Assessment")
    print("=" * 60)
    
    if not os.path.exists("clean_articles"):
        print("Error: clean_articles directory not found!")
        print("Please run the article searchers first.")
        return
    
    choice = input("""
Choose an option:
1. Scrape all URLs and create comprehensive summaries
2. Show what URLs would be scraped
3. Exit

Enter choice (1-3): """).strip()
    
    if choice == "1":
        process_all_urls()
    elif choice == "2":
        urls_data = extract_urls_from_files()
        if urls_data:
            print(f"\nFound {len(urls_data)} URLs:")
            for i, url_data in enumerate(urls_data, 1):
                print(f"{i:3d}. {url_data['url']}")
                print(f"     Query: {url_data['search_query']}")
                print(f"     Borrower: {url_data['borrower_id']}")
                print()
        else:
            print("No URLs found")
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
