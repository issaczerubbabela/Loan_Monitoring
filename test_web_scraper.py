#!/usr/bin/env python3
"""
Test the web scraper with a few sample URLs
"""
import os
from advanced_web_scraper import extract_urls_from_files, scrape_website_content, create_comprehensive_summary

def test_url_extraction():
    """Test URL extraction from article files"""
    print("Testing URL extraction...")
    urls_data = extract_urls_from_files("clean_articles")
    
    if urls_data:
        print(f"✓ Found {len(urls_data)} URLs")
        print("\nFirst 5 URLs:")
        for i, url_data in enumerate(urls_data[:5], 1):
            print(f"{i}. {url_data['url']}")
            print(f"   Query: {url_data['search_query']}")
            print(f"   Borrower: {url_data['borrower_id']}")
            print()
    else:
        print("✗ No URLs found")
    
    return urls_data

def test_single_scrape():
    """Test scraping a single URL"""
    urls_data = extract_urls_from_files("clean_articles")
    
    if not urls_data:
        print("No URLs to test")
        return
    
    # Test with first URL
    test_url_data = urls_data[0]
    print(f"\nTesting scrape of: {test_url_data['url']}")
    print(f"Query: {test_url_data['search_query']}")
    
    # Scrape content
    web_content = scrape_website_content(test_url_data['url'])
    
    if web_content['status'] == 'success':
        print(f"✓ Successfully scraped {web_content['content_length']} characters")
        print(f"  Title: {web_content['title']}")
        print(f"  Content preview: {web_content['content'][:200]}...")
        
        # Test Gemini summary
        print("\nTesting Gemini summary...")
        summary = create_comprehensive_summary(test_url_data, web_content)
        print(f"✓ Summary created ({len(summary)} characters)")
        print(f"  Summary preview: {summary[:200]}...")
        
    else:
        print(f"✗ Failed to scrape: {web_content.get('error', 'Unknown error')}")

def main():
    """Main test function"""
    print("Web Scraper Test Suite")
    print("=" * 40)
    
    # Test URL extraction
    urls_data = test_url_extraction()
    
    if urls_data:
        proceed = input("\nTest scraping a single URL? (y/n): ").lower().strip()
        if proceed == 'y':
            test_single_scrape()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
