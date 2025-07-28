#!/usr/bin/env python3
"""
Test script for the new Playwright-based search functionality
"""

from loan_repay_predictor import search_web

def test_search():
    """Test the search_web function with a sample query"""
    print("Testing Playwright-based search with Gemini ranking...")
    
    # Test query
    test_query = "Tesla stock performance future outlook"
    
    try:
        results = search_web(test_query, borrower_id="test", num_results=3)
        
        print(f"\nSearch results for: '{test_query}'")
        print("=" * 50)
        print(results)
        
        if results:
            print("\n✅ Search completed successfully!")
            print(f"Results saved to articles/test_{test_query.replace(' ', '_')[:50]}.txt")
        else:
            print("\n❌ No results returned")
            
    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        print("\nMake sure you have:")
        print("1. Installed Playwright: pip install playwright")
        print("2. Installed browsers: playwright install chromium")
        print("3. Set up your GEMINI_KEY in keys.py")

if __name__ == "__main__":
    test_search()
