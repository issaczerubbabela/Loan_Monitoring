#!/usr/bin/env python3
"""
Debug script to test web scraping functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loan_repay_predictor import scrape_search_results, scrape_duckduckgo_results

def test_google_search():
    """Test Google search scraping"""
    print("=" * 50)
    print("Testing Google Search")
    print("=" * 50)
    
    query = "Tesla stock performance 2025"
    results = scrape_search_results(query, num_results=5)
    
    print(f"\nResults for '{query}':")
    if results:
        for i, article in enumerate(results, 1):
            print(f"\n{i}. Title: {article['title']}")
            print(f"   Link: {article['link']}")
            print(f"   Snippet: {article['snippet'][:100]}...")
    else:
        print("No results found")
    
    return len(results) > 0

def test_duckduckgo_search():
    """Test DuckDuckGo search scraping"""
    print("\n" + "=" * 50)
    print("Testing DuckDuckGo Search")
    print("=" * 50)
    
    query = "Tesla stock performance 2025"
    results = scrape_duckduckgo_results(query, num_results=5)
    
    print(f"\nResults for '{query}':")
    if results:
        for i, article in enumerate(results, 1):
            print(f"\n{i}. Title: {article['title']}")
            print(f"   Link: {article['link']}")
            print(f"   Snippet: {article['snippet'][:100]}...")
    else:
        print("No results found")
    
    return len(results) > 0

def main():
    """Run all tests"""
    print("🔍 Web Scraping Debug Tests")
    print("This will help identify why searches are failing")
    
    # Test Google
    google_success = test_google_search()
    
    # Test DuckDuckGo
    duckduckgo_success = test_duckduckgo_search()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Google Search: {'✅ SUCCESS' if google_success else '❌ FAILED'}")
    print(f"DuckDuckGo Search: {'✅ SUCCESS' if duckduckgo_success else '❌ FAILED'}")
    
    if not google_success and not duckduckgo_success:
        print("\n🚨 Both search methods failed!")
        print("Possible issues:")
        print("1. Network connectivity problems")
        print("2. Playwright browser not installed (run: playwright install chromium)")
        print("3. Anti-bot measures by search engines")
        print("4. Changes in search engine HTML structure")
        print("\nTry running: python setup_playwright.py")
    
    elif google_success or duckduckgo_success:
        print("\n✅ At least one search method is working!")
        print("The loan monitoring system should work correctly.")

if __name__ == "__main__":
    main()
