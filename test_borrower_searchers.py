#!/usr/bin/env python3
"""
Test script for borrower-specific article searchers
"""
import os
import pandas as pd
import time
from borrower_ddg_searcher import process_borrower_ddg
from borrower_serp_searcher import process_borrower_serp, check_serpapi_quota

def test_single_borrower():
    """Test both searchers on a single borrower"""
    
    # Read CSV and get first borrower
    try:
        df = pd.read_csv("loan_data.csv")
        if len(df) == 0:
            print("No borrowers found in loan_data.csv")
            return
        
        borrower = df.iloc[0]  # Get first borrower
        
        print("=" * 80)
        print("TESTING BORROWER-SPECIFIC ARTICLE SEARCHERS")
        print("=" * 80)
        
        print(f"Test Borrower: {borrower['borrower_name']} (ID: {borrower['borrower_id']})")
        print(f"Job: {borrower['job_title']} at {borrower['company']} ({borrower['industry']})")
        print()
        
        # Check SerpAPI quota
        print("Checking SerpAPI quota...")
        quota_ok = check_serpapi_quota()
        print()
        
        # Test DuckDuckGo searcher
        print("1. Testing DuckDuckGo Borrower Searcher")
        print("-" * 50)
        try:
            ddg_files = process_borrower_ddg(borrower, "clean_articles")
            print(f"✓ DuckDuckGo search completed: {len(ddg_files)} files saved")
        except Exception as e:
            print(f"✗ DuckDuckGo search error: {e}")
        
        print()
        time.sleep(5)  # Pause between searches
        
        # Test SerpAPI searcher
        print("2. Testing SerpAPI Borrower Searcher")
        print("-" * 50)
        try:
            serp_files = process_borrower_serp(borrower, "clean_articles")
            print(f"✓ SerpAPI search completed: {len(serp_files)} files saved")
        except Exception as e:
            print(f"✗ SerpAPI search error: {e}")
        
        print()
        print("=" * 80)
        print("TEST COMPLETED")
        print("=" * 80)
        
        # Show generated files
        show_generated_files()
        
    except Exception as e:
        print(f"Error: {e}")

def show_generated_files():
    """Show files generated in clean_articles folder"""
    output_dir = "clean_articles"
    if os.path.exists(output_dir):
        print(f"\nFiles in {output_dir}:")
        files = os.listdir(output_dir)
        if files:
            for file in sorted(files):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  - {file} ({file_size} bytes)")
        else:
            print("  No files found")
    else:
        print(f"\n{output_dir} directory does not exist")

def test_query_generation():
    """Test query generation for borrowers"""
    try:
        df = pd.read_csv("loan_data.csv")
        
        print("=" * 80)
        print("TESTING QUERY GENERATION")
        print("=" * 80)
        
        for index, borrower in df.iterrows():
            print(f"\nBorrower {borrower['borrower_id']}: {borrower['borrower_name']}")
            print(f"Job: {borrower['job_title']} at {borrower['company']} ({borrower['industry']})")
            print("Generated Queries:")
            
            # Import the query generation function
            from borrower_ddg_searcher import generate_queries
            queries = generate_queries(borrower['job_title'], borrower['company'], borrower['industry'])
            
            for i, query in enumerate(queries, 1):
                print(f"  {i:2d}. {query}")
            
            if index >= 2:  # Show only first 3 borrowers
                break
    
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    print("Borrower Article Searcher Test Suite")
    print("=" * 60)
    
    if not os.path.exists("loan_data.csv"):
        print("Error: loan_data.csv not found!")
        return
    
    choice = input("""
Choose test option:
1. Test single borrower (both DDG and SerpAPI)
2. Show query generation for all borrowers
3. Exit

Enter choice (1-3): """).strip()
    
    if choice == "1":
        test_single_borrower()
    elif choice == "2":
        test_query_generation()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
