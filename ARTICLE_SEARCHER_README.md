# Article Searcher Tools

This repository contains two powerful article search tools that use different search engines, rank results with Google's Gemini AI, and save clean, summarized articles as text files.

## Files

1. **`ddg_article_searcher.py`** - Uses DuckDuckGo search with web scraping
2. **`serpapi_article_searcher.py`** - Uses Google Search via SerpAPI
3. **`test_article_searchers.py`** - Test script to demonstrate both tools
4. **`clean_articles/`** - Output directory for generated article summaries

## Features

- **Multi-source search**: DuckDuckGo (free) and Google via SerpAPI (paid)
- **AI-powered ranking**: Uses Gemini AI to rank search results by relevance
- **Clean summaries**: Generates comprehensive, well-structured article summaries
- **Automated saving**: Saves results as clean text files with metadata
- **Error handling**: Robust error handling and fallback mechanisms

## Setup

1. **Install dependencies**:
   ```bash
   pip install playwright requests google-generativeai
   playwright install chromium
   ```

2. **Configure API keys** in `keys.py`:
   ```python
   SERP_KEY = "your_serpapi_key_here"
   GEMINI_KEY = "your_gemini_api_key_here"
   ```

## Usage

### Option 1: Use individual scripts

#### DuckDuckGo Searcher (Free)
```bash
python ddg_article_searcher.py
```

#### SerpAPI Searcher (Paid, more reliable)
```bash
python serpapi_article_searcher.py
```

### Option 2: Test both tools
```bash
python test_article_searchers.py
```

### Option 3: Use as Python modules

```python
from ddg_article_searcher import search_and_save_articles as ddg_search
from serpapi_article_searcher import search_and_save_articles as serp_search

# Search with DuckDuckGo
ddg_search("artificial intelligence trends 2025", top_k=5)

# Search with SerpAPI
serp_search("electric vehicle adoption 2024", top_k=5)
```

## Function Parameters

### `search_and_save_articles(query, output_dir="clean_articles", top_k=5)`

- **`query`** (str): Search query
- **`output_dir`** (str): Directory to save results (default: "clean_articles")
- **`top_k`** (int): Number of top articles to include in summary (default: 5)

## Output Format

Each search generates a text file with:

1. **Header**: Query, search engine, date, and metadata
2. **AI Summary**: Comprehensive summary combining insights from all sources
3. **Source Articles**: List of original articles with titles, URLs, and snippets

### Example Output Structure
```
Search Query: artificial intelligence job market 2025
Search Engine: Google (via SerpAPI)
Date: 2024-12-19 15:30:45
Top 5 articles selected and summarized
================================================================================

[AI-GENERATED COMPREHENSIVE SUMMARY]

================================================================================
SOURCE ARTICLES:

1. AI Job Market Outlook 2025: What to Expect
   URL: https://example.com/ai-jobs-2025
   Snippet: The AI job market is experiencing unprecedented growth...

2. Future of Work: AI's Impact on Employment
   URL: https://example.com/future-work-ai
   Snippet: Artificial intelligence is reshaping the employment landscape...
```

## API Costs

- **DuckDuckGo**: Free (web scraping)
- **SerpAPI**: Paid service (~$50/month for 5,000 searches)

## Features Comparison

| Feature | DuckDuckGo | SerpAPI |
|---------|------------|---------|
| Cost | Free | Paid |
| Reliability | Moderate | High |
| Rate Limits | None | API limits |
| Search Quality | Good | Excellent |
| News Results | Limited | Included |
| Structured Data | Basic | Rich |

## Best Practices

1. **Use SerpAPI for production**: More reliable and provides better structured data
2. **Use DuckDuckGo for testing**: Free and good for development
3. **Monitor API usage**: Check SerpAPI quota regularly
4. **Respect rate limits**: Built-in delays prevent overwhelming servers
5. **Review summaries**: AI-generated summaries should be reviewed for accuracy

## Error Handling

Both tools include comprehensive error handling:
- Network timeouts
- API rate limits
- Parsing errors
- File system issues
- Gemini API failures

## Customization

You can easily customize:
- Search parameters
- Number of results
- Output format
- Gemini prompts
- File naming conventions

## Example Queries

- "artificial intelligence job market 2025"
- "electric vehicle adoption trends 2024"
- "remote work future predictions"
- "cryptocurrency regulation updates 2024"
- "climate change impact on agriculture"
- "renewable energy investment opportunities"

## Troubleshooting

### Common Issues

1. **Playwright browser not found**:
   ```bash
   playwright install chromium
   ```

2. **SerpAPI quota exceeded**:
   - Check your usage at https://serpapi.com/account
   - Upgrade your plan if needed

3. **Gemini API errors**:
   - Verify your API key in `keys.py`
   - Check quota at https://makersuite.google.com/

4. **DuckDuckGo scraping fails**:
   - Site structure may have changed
   - Try using SerpAPI instead

### Support

For issues or questions:
1. Check the error messages in the console
2. Verify API keys are correct
3. Ensure all dependencies are installed
4. Test with the provided test script

## License

This project is open source. Feel free to modify and adapt for your needs.
