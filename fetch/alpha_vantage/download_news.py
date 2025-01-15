

def get_relevance_score(news_item, ticker):

    """Filters news based on relevance"""

    for item in news_item["ticker_sentiment"]:
        if item["ticker"] == ticker:
            return float(item["relevance_score"])
    return 0




    

