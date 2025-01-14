import requests
import datetime
import re
import yfinance as yf
from heapq import *


def get_usa_news(ticker):
    news = []
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey=JIHXVRY5SPIH16C9"
    r = requests.get(url)
    data = r.json()
    for news_item in data["feed"]:
        if news_item["source"] in ["CNBC", "Money Morning", "Motley Fool", "South China Morning Post", "Zacks Commentary"]:
            relevance_score = get_relevance_score(news_item, ticker)
            if relevance_score > 0.35:
                #using maxheap, sort by relevance, default mode sorts by date
                heappush(news, (-relevance_score, news_item))
    return news

def get_relevance_score(news_item, ticker):

    """Filters news based on relevance"""

    for item in news_item["ticker_sentiment"]:
        if item["ticker"] == ticker:
            return float(item["relevance_score"])
    return 0




    

