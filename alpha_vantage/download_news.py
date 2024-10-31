import requests

def download_av_news(db_ticker):

    """Downloads news from Alpha Vantage. Currently, only USA functionality"""

    exchange = db_ticker.exchange
    ticker = db_ticker.ticker
    if exchange in ["NYSE", "NASDAQ", "NYQ", "NYE"]:
        news = get_usa_news(ticker)
        return news
    else:
        print("Functionality not available yet")
        return []

def get_usa_news(ticker):
    news = []
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey=JIHXVRY5SPIH16C9"
    r = requests.get(url)
    data = r.json()
    for news_item in data["feed"]:
        if news_item["source"] in ["CNBC", "Money Morning", "Motley Fool", "South China Morning Post", "Zacks Commentary"]:
            relevance_score = get_relevance_score(news_item, ticker)
            if relevance_score > 0.4:
                news.append(news_item)
    return news

def get_relevance_score(news_item, ticker):
    for item in news["ticker_sentiment"]:
        if item["ticker"] == ticker:
            return float(item["relevance_score"])
    return 0