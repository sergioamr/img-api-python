import re
import os
import json
from datetime import datetime
from heapq import *

from imgapi.imgapi import ImgAPI
from colorama import Fore, Back, Style, init

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from thelpers import *
from alpha_vantage.news_extractor_helpers import *
from alpha_vantage.download_news import *
from google.download_news import *
from google.news_extractor_helpers import *

init(autoreset=True)

api = ImgAPI()

api.setup(config_file="config.json")


######################## ALPHAVANTAGE
def discover_av_news(ticker, db_ticker = None, test = True):
    if db_ticker:
        ticker = db_ticker.ticker
        exchange = db_ticker.symbol
        if exchange in ["NYSE", "NASDAQ", "NYQ", "NYE"]:
            av_news = get_usa_news(ticker)
    else:
        av_news = get_usa_news(ticker)
    return av_news

#av_news is a heap data structure that prioritizes the most relevant articles for processing
def add_to_waiting_index(av_news):
    while av_news:
        relevance, news = heappop(av_news)

        uuid = generate_uuid(news)
        api_params = f"?external_uuid={uuid}&source=ALPHAVANTAGE"
        found = api.api_call("/news/query" + api_params)
        
        #if article already in database, continue
        if len(found["news"]) > 0:
            print("news found", found["news"])
            continue

        related_exchange_tickers = []
        for ticker in news["ticker_sentiment"]:
            if float(ticker["relevance_score"]) > 0.29:
                #format tickers into sergio's format
                related_exchange_tickers.append(format_ticker(ticker["ticker"]))
    
        article = {
                "articles": [],
                "creation_date": parse_av_dates(news["time_published"]),
                "external_uuid": uuid,
                "link": news["url"],
                "publisher": news["source"],
                "related_exchange_tickers": related_exchange_tickers,
                "source": "ALPHAVANTAGE",
                "status": "WAITING_INDEX",
            "title": news["title"]
            }
        
        res = api.api_call("/news/create", data = article)
        
av_news = discover_av_news("NVDA")
add_to_waiting_index(av_news)