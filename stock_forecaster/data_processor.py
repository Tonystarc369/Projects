import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_stock_data(ticker, days=365):
    """Fetches historical price data using Yahoo Finance API."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Download data
    df = yf.download(ticker, start=start_date, end=end_date)
    
    # Clean up multi-index columns if yfinance returns them formatted that way
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    return df.reset_index()

def fetch_news_sentiment(ticker):
    """Fetches live headlines and uses Natural Language Processing to score sentiment."""
    if not NEWS_API_KEY or NEWS_API_KEY == "your_actual_news_api_key_here":
        return 0.0 # Return neutral if key is missing
    
    url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&sortBy=publishedAt&pageSize=20&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])
        
        if not articles:
            return 0.0
            
        scores = []
        for article in articles:
            # Combine headline title and summary snippet for processing
            content = f"{article.get('title', '')} {article.get('description', '')}"
            analysis = TextBlob(content)
            scores.append(analysis.sentiment.polarity)
            
        # Return mathematical average of all article polarities
        return sum(scores) / len(scores)
        
    except Exception:
        return 0.0