# Borrower Risk Assessment Article Searchers

This system provides specialized article search tools for loan risk assessment, designed to analyze borrowers' employment and industry stability by searching for relevant articles about their companies, job roles, and industries.

## 🎯 **Purpose**

These tools help assess loan repayment risk by gathering external market intelligence about:
- Company stock performance and financial health
- Industry recession/growth predictions
- Job automation risks
- Skill obsolescence trends
- Regional economic factors
- Educational cost projections

## 📁 **Files**

### **Core Searchers**
- **`borrower_ddg_searcher.py`** - DuckDuckGo-based searcher (free)
- **`borrower_serp_searcher.py`** - SerpAPI-based searcher (paid, more reliable)
- **`test_borrower_searchers.py`** - Test suite for both searchers

### **Data**
- **`loan_data.csv`** - Borrower information database
- **`clean_articles/`** - Output directory for search results

## 🔍 **Search Queries Generated**

For each borrower, the system generates 12 specific queries:

1. `{company} stock performance 5-year outlook`
2. `{industry} recession or growth prediction 5 years`
3. `{job_title} automation risk in 5 years`
4. `{industry} job market demand 5 years ahead`
5. `{company} acquisition merger possibility in 5 years`
6. `{company} product relevance in 5 years`
7. `{job_title} skill obsolescence trend over next 5 years`
8. `replaceability of {job_title} aged 40 in {industry}`
9. `pollution projection for {industry} region in 5 years`
10. `disease risk in high-pollution zones in {industry} region`
11. `cost of college education in {industry} region over next 5 years`
12. `financial burden of children entering college in {industry} region`

## 📊 **Input Data Format**

The system expects a CSV file (`loan_data.csv`) with these columns:

```csv
borrower_id,borrower_name,loan_amount,loan_start_year,job_title,company,industry,repayments_on_time,late_payments,avg_days_late
101,Jane Doe,15000,2020,Software Engineer,Infosys,IT,36,0,0
102,John Smith,25000,2020,Mechanical Engineer,Bosch,Automotive,30,6,12
```

## 🚀 **How to Use**

### **Option 1: Process All Borrowers**

#### DuckDuckGo (Free)
```bash
python borrower_ddg_searcher.py
```

#### SerpAPI (Paid)
```bash
python borrower_serp_searcher.py
```

### **Option 2: Test Single Borrower**
```bash
python test_borrower_searchers.py
```

### **Option 3: Use as Python Module**

```python
import pandas as pd
from borrower_ddg_searcher import process_borrower_ddg
from borrower_serp_searcher import process_borrower_serp

# Load borrower data
df = pd.read_csv("loan_data.csv")
borrower = df.iloc[0]  # First borrower

# Process with DuckDuckGo
ddg_files = process_borrower_ddg(borrower)

# Process with SerpAPI
serp_files = process_borrower_serp(borrower)
```

## 📈 **Processing Scale**

- **Per Borrower**: 12 searches (one per risk factor)
- **Per Search**: Top 3 ranked articles saved
- **Example**: 10 borrowers = 120 searches = 360 articles

## 💾 **Output Format**

Each search creates a separate text file:

### **File Naming**
- DuckDuckGo: `DDG_{borrower_id}_{safe_query}.txt`
- SerpAPI: `SERP_{borrower_id}_{safe_query}.txt`

### **File Content**
```
Search Query: Infosys stock performance 5-year outlook
Search Engine: Google (via SerpAPI)
Date: 2024-12-19 15:30:45
Borrower ID: 101
================================================================================

1. Infosys Share Price Target 2025: Expert Analysis
   URL: https://example.com/infosys-analysis
   Summary: Infosys stock shows strong fundamentals with projected growth...

2. IT Sector Growth Prospects Through 2029
   URL: https://example.com/it-sector-outlook
   Summary: The Indian IT sector is expected to maintain steady growth...

3. Infosys Q4 Results: Revenue and Profit Margins
   URL: https://example.com/infosys-q4-results
   Summary: Infosys reported strong quarterly results with increased...
```

## 🔧 **Features**

### **AI-Powered Ranking**
- Uses Gemini AI to rank search results by relevance
- Considers title match, content relevance, and source credibility
- Automatically selects top 3 most relevant articles

### **Robust Error Handling**
- Continues processing even if individual searches fail
- Graceful handling of API rate limits
- Automatic retries for network issues

### **Progress Tracking**
- Real-time progress updates
- Summary of successful vs. failed searches
- File count and size reporting

## 💰 **Cost Considerations**

### **DuckDuckGo Searcher**
- **Cost**: Free
- **Reliability**: Moderate (depends on web scraping)
- **Rate Limits**: None
- **Best For**: Testing and development

### **SerpAPI Searcher**
- **Cost**: ~$50/month for 5,000 searches
- **Reliability**: High (official Google API)
- **Rate Limits**: Based on plan
- **Best For**: Production use

### **Cost Calculation**
- 10 borrowers × 12 queries = 120 searches
- 100 borrowers × 12 queries = 1,200 searches
- SerpAPI cost: ~$12-15 per 100 borrowers

## ⚙️ **Configuration**

### **API Keys** (in `keys.py`)
```python
SERP_KEY = "your_serpapi_key_here"
GEMINI_KEY = "your_gemini_api_key_here"
```

### **Customizable Parameters**
- `years_ahead`: Prediction timeframe (default: 5 years)
- `top_k`: Number of articles per search (default: 3)
- `num_results`: Search results to analyze (default: 10)
- `output_dir`: Output directory (default: "clean_articles")

## 🛠️ **Setup**

1. **Install dependencies**:
   ```bash
   pip install pandas playwright requests google-generativeai
   playwright install chromium
   ```

2. **Configure API keys** in `keys.py`

3. **Prepare borrower data** in `loan_data.csv`

4. **Run the searchers**:
   ```bash
   python test_borrower_searchers.py  # Test first
   python borrower_ddg_searcher.py    # Process all (free)
   python borrower_serp_searcher.py   # Process all (paid)
   ```

## 📊 **Integration with Loan System**

The generated articles can be integrated with your main loan prediction system:

```python
# In your main loan_repay_predictor.py
def collect_borrower_articles(borrower_id):
    """Collect all articles for a borrower"""
    articles_dir = "clean_articles"
    borrower_files = [f for f in os.listdir(articles_dir) 
                     if f.startswith(f"SERP_{borrower_id}_")]
    
    combined_content = ""
    for file in borrower_files:
        with open(os.path.join(articles_dir, file), 'r') as f:
            combined_content += f.read() + "\n\n"
    
    return combined_content

# Use in your risk assessment
borrower_articles = collect_borrower_articles(101)
summary = summarize_external_signals(company, job, industry, borrower_articles)
```

## 🔄 **Automation Options**

### **Scheduled Processing**
```python
# Run daily/weekly to update articles
import schedule
import time

def process_all_borrowers():
    from borrower_serp_searcher import process_borrowers_from_csv
    process_borrowers_from_csv("loan_data.csv")

schedule.every().week.do(process_all_borrowers)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### **Incremental Processing**
```python
# Process only new borrowers
def process_new_borrowers():
    # Logic to identify new borrowers since last run
    # Process only those borrowers
    pass
```

## 🔍 **Example Queries Generated**

For **Jane Doe** (Software Engineer at Infosys in IT industry):

1. `Infosys stock performance 5-year outlook`
2. `IT recession or growth prediction 5 years`
3. `Software Engineer automation risk in 5 years`
4. `IT job market demand 5 years ahead`
5. `Infosys acquisition merger possibility in 5 years`
6. `Infosys product relevance in 5 years`
7. `Software Engineer skill obsolescence trend over next 5 years`
8. `replaceability of Software Engineer aged 40 in IT`
9. `pollution projection for IT region in 5 years`
10. `disease risk in high-pollution zones in IT region`
11. `cost of college education in IT region over next 5 years`
12. `financial burden of children entering college in IT region`

## 🎯 **Risk Assessment Integration**

The collected articles provide intelligence for:

- **Employment Risk**: Job automation, skill obsolescence
- **Company Risk**: Financial health, acquisition likelihood
- **Industry Risk**: Growth/recession predictions, market demand
- **Regional Risk**: Environmental and economic factors
- **Future Costs**: Education expenses, healthcare costs

## 📞 **Support**

For issues or questions:
1. Check console output for error messages
2. Verify API keys are correctly set
3. Ensure CSV file format matches requirements
4. Test with single borrower first
5. Monitor API quota usage

## 🔒 **Security Notes**

- Store API keys securely (not in version control)
- Consider rate limiting for large-scale processing
- Monitor API usage and costs
- Implement proper error logging for production use
