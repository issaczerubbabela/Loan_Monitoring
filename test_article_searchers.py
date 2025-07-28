#!/usr/bin/env python3
"""
Test script to demonstrate the article searcher tools
"""
import sys
import os
import time
from ddg_article_searcher import search_and_save_articles as ddg_search
from serpapi_article_searcher import search_and_save_articles as serp_search, check_serpapi_quota

def test_both_searchers():
    """Test both DuckDuckGo and SerpAPI searchers with a sample query"""
    
    test_query = "artificial intelligence job market 2025"
    
    print("=" * 80)
    print("TESTING ARTICLE SEARCHER TOOLS")
    print("=" * 80)
    
    print(f"Test query: {test_query}")
    print()
    
    # Check SerpAPI quota first
    print("Checking SerpAPI quota...")
    quota_ok = check_serpapi_quota()
    print()
    
    # Test DuckDuckGo searcher
    print("1. Testing DuckDuckGo Article Searcher")
    print("-" * 40)
    try:
        ddg_result = ddg_search(test_query, top_k=3)
        if ddg_result:
            print(f"✓ DuckDuckGo search completed successfully")
            print(f"  Result saved to: {ddg_result}")
        else:
            print("✗ DuckDuckGo search failed")
    except Exception as e:
        print(f"✗ DuckDuckGo search error: {e}")
    
    print()
    time.sleep(3)  # Brief pause between searches
    
    # Test SerpAPI searcher
    print("2. Testing SerpAPI Article Searcher")
    print("-" * 40)
    try:
        serp_result = serp_search(test_query, top_k=3)
        if serp_result:
            print(f"✓ SerpAPI search completed successfully")
            print(f"  Result saved to: {serp_result}")
        else:
            print("✗ SerpAPI search failed")
    except Exception as e:
        print(f"✗ SerpAPI search error: {e}")
    
    print()
    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
    
    # Show output directory contents
    output_dir = "clean_articles"
    if os.path.exists(output_dir):
        print(f"\nFiles in {output_dir}:")
        files = os.listdir(output_dir)
        for file in files:
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file} ({file_size} bytes)")
    
    print("\nYou can now check the generated files in the 'clean_articles' folder.")

if __name__ == "__main__":
    test_both_searchers()
