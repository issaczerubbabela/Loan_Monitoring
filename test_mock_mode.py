#!/usr/bin/env python3
"""
Manual test mode for loan monitoring without web scraping
This creates mock articles to test the rest of the pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loan_repay_predictor import *
import pandas as pd

def create_mock_articles(query):
    """Create mock articles for testing purposes"""
    mock_articles = {
        "stock performance": [
            {
                'title': 'Company Stock Analysis 2025: Growth Prospects and Market Outlook',
                'snippet': 'Financial analysts predict strong growth potential with revenue increasing 15% year-over-year. Market conditions favor technology stocks with robust fundamentals.',
                'link': 'https://example.com/stock-analysis-2025'
            },
            {
                'title': 'Market Volatility Concerns: Stock Performance Under Pressure',
                'snippet': 'Recent market turbulence has impacted stock prices across sectors. Investors remain cautious about near-term performance amid economic uncertainty.',
                'link': 'https://example.com/market-volatility-analysis'
            }
        ],
        "recession": [
            {
                'title': 'Economic Recession Predictions for 2025: Industry Impact Analysis',
                'snippet': 'Economists forecast mild recession risk with selective industry impacts. Technology and healthcare sectors show resilience while manufacturing faces challenges.',
                'link': 'https://example.com/recession-analysis-2025'
            }
        ],
        "automation": [
            {
                'title': 'Job Automation Trends: Which Roles Are Most At Risk?',
                'snippet': 'Artificial intelligence and automation technologies are reshaping the job market. Routine tasks face highest displacement risk while creative roles remain secure.',
                'link': 'https://example.com/automation-job-impact'
            }
        ],
        "job market": [
            {
                'title': 'Job Market Demand Forecast 2025: Growth Sectors and Opportunities',
                'snippet': 'Employment outlook shows continued growth in technology, healthcare, and renewable energy sectors. Remote work trends create new opportunities.',
                'link': 'https://example.com/job-market-forecast-2025'
            }
        ],
        "acquisition": [
            {
                'title': 'Corporate Merger and Acquisition Activity Surges in 2025',
                'snippet': 'M&A activity reaches new highs as companies seek strategic consolidation. Technology acquisitions drive market activity with valuations remaining elevated.',
                'link': 'https://example.com/ma-activity-2025'
            }
        ],
        "product relevance": [
            {
                'title': 'Product Innovation and Market Relevance: 2030 Technology Trends',
                'snippet': 'Emerging technologies reshape product landscapes. Companies investing in AI, sustainability, and digital transformation maintain competitive advantage.',
                'link': 'https://example.com/product-innovation-2030'
            }
        ],
        "skill obsolescence": [
            {
                'title': 'Skill Evolution in the Digital Age: Staying Relevant',
                'snippet': 'Traditional skills face obsolescence as digital transformation accelerates. Continuous learning and adaptation become critical for career sustainability.',
                'link': 'https://example.com/skill-evolution-digital-age'
            }
        ]
    }
    
    # Find relevant mock articles based on query keywords
    relevant_articles = []
    query_lower = query.lower()
    
    for category, articles in mock_articles.items():
        if any(keyword in query_lower for keyword in category.split()):
            relevant_articles.extend(articles)
    
    # If no specific match, return a generic article
    if not relevant_articles:
        relevant_articles = [{
            'title': f'Analysis: {query}',
            'snippet': 'Market analysis indicates mixed signals with both opportunities and challenges present in the current economic environment.',
            'link': 'https://example.com/generic-analysis'
        }]
    
    return relevant_articles[:3]  # Return up to 3 articles

def mock_search_web(query, borrower_id=None, num_results=3):
    """Mock search function using predefined articles"""
    print(f"🔧 MOCK MODE: Searching for: {query}")
    
    # Get mock articles
    articles = create_mock_articles(query)
    
    # Format articles for output
    formatted_articles = []
    for article in articles[:num_results]:
        formatted_articles.append(f"{article['title']}\n{article['snippet']}\n{article['link']}")
    
    # Save articles to file
    safe_query = re.sub(r'[^\w\s-]', '', query).replace(' ', '_')[:50]
    filename = f"articles/{borrower_id}_{safe_query}_MOCK.txt" if borrower_id else f"articles/{safe_query}_MOCK.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== MOCK DATA FOR TESTING ===\n\n")
            f.write("\n\n".join(formatted_articles))
        print(f"Saved mock articles to {filename}")
    except Exception as e:
        print(f"Error saving mock articles: {e}")
    
    return "\n\n".join(formatted_articles)

def test_with_mock_data():
    """Test the entire pipeline with mock data"""
    print("🧪 Testing loan monitoring pipeline with mock data...")
    
    # Replace the real search function temporarily
    import loan_repay_predictor
    original_search = loan_repay_predictor.search_web
    loan_repay_predictor.search_web = mock_search_web
    
    try:
        # Test with sample borrower data
        sample_data = {
            'job_title': ['Software Engineer', 'Data Analyst'],
            'company': ['Tesla', 'Meta'],
            'industry': ['Automotive', 'Technology']
        }
        
        df = pd.DataFrame(sample_data)
        
        print("\nProcessing sample borrowers...")
        results = []
        for _, row in df.iterrows():
            print(f"\nProcessing: {row['job_title']} at {row['company']}")
            risk_score, explanation = process_borrower(row)
            results.append({
                'job_title': row['job_title'],
                'company': row['company'],
                'industry': row['industry'],
                'risk_score': risk_score,
                'explanation': explanation[:200] + "..." if len(explanation) > 200 else explanation
            })
        
        # Display results
        print("\n" + "="*80)
        print("MOCK TEST RESULTS")
        print("="*80)
        
        for result in results:
            print(f"\n👤 {result['job_title']} at {result['company']}")
            print(f"🏭 Industry: {result['industry']}")
            print(f"⚠️  Risk Score: {result['risk_score']}")
            print(f"📝 Explanation: {result['explanation']}")
            print("-" * 60)
        
        print("\n✅ Mock test completed successfully!")
        print("The pipeline is working. The issue is likely with web scraping.")
        
    finally:
        # Restore original search function
        loan_repay_predictor.search_web = original_search

if __name__ == "__main__":
    test_with_mock_data()
