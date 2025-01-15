import re
import random
import os
import json
from datetime import datetime
from heapq import *
import asyncio
from crawl4ai import AsyncWebCrawler
from googlenewsdecoder import new_decoderv1

from urllib.parse import quote_plus
from imgapi.imgapi import ImgAPI
#from imgapi.print_tools import *
from colorama import Fore, Back, Style, init

from thelpers import *
from fetch.google.download_news import *
from fetch.google.news_extractor_helpers import *
from datetime import date

init(autoreset=True)

api = ImgAPI()
api.setup(config_file="config.json")

def print_b(text):
    print(Fore.BLUE + text)


def print_g(text):
    print(Fore.GREEN + text)


def print_r(text):
    print(Fore.RED + text)


def print_e(text):
    print(Back.RED +
          "************************************************************")
    print(Back.RED + text)
    print(Back.RED +
          "************************************************************")


def print_exception(err, text=''):
    import traceback
    print(Fore.RED + str(err))
    traceback.print_tb(err.__traceback__)



class google_pipeline:
    def get_uuid(self, item, ticker):
        date = parse_google_dates(item["published"])
        return f"G_{ticker}_{item['source']['title'][0]}_{date}"

    def prepare_schema(self, item, ticker):
        converged = True
        while converged:
            try:
                link = new_decoderv1(item["link"])
                url = link["decoded_url"]
                converged = False
            #KeyError occurs when new_decoderv1 throws a 429 error
            except KeyError:
                time.sleep(500)
                converged = True
        news_item = {
                "articles": [],
                "creation_date": parse_google_dates(item["published"]),
                "experiment": "ordersofmagnitudenikki",
                "external_uuid": self.get_uuid(item, ticker),
                "link": url,
                "publisher": item["source"]["title"],
                "related_exchange_tickers": [format_ticker(ticker)],
                "source": "GOOGLE",
                "status": "WAITING_INDEX",
            "title": item["title"]
            }
        return news_item

    def cache_news(self, news_arr, ticker):
        today = date.today()
        folder_path = os.path.join("google_cache", str(today))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        with open(f"google_cache/{today}/{ticker}", "w") as f:
            json.dump(news_arr, f, indent= 4)
        return

    def discover_google_news(self, ticker):

        """Google news discovery. Returns news_arr, an array of dicts"""
        
        news_arr = []
        gn = GoogleNews()

        #getting company name
        company = get_company_name_from_ticker(ticker)

        #news discovery
        search = gn.search(f"{company} ({ticker})")
        for item in search["entries"]:
            if item["source"]["title"] in ["Forbes", "ForexLive", "Fortune", "Investor's Business Daily", "Investopedia", "Investing.com", "Simply Wall St", "StockTitan"]:
                #check if news in database
                if self.is_indexed(item):
                    continue
                #prepare data schema & append into news_arr
                news_item = self.prepare_schema(item, ticker)
                news_arr.append(news_item)
        #cache the news
        self.cache_news(news_arr, ticker)
        return news_arr

    def is_indexed(self, item):

        """Checks if news_item is present in database. Returns True if it is in database,
        False otherwise."""

        api_params = f"?external_uuid={item['id']}&source=GOOGLE"
        api.api_entry = "http://dev.gputop.com/api"
        found = api.api_call("/news/query" + api_params)
        
        if len(found["news"]) > 0:
            print_r(f"News already in database!")
            return True
        else:
            return False

    def read_from_cache(self, ticker):
        
        """Reads data from cache and returns"""

        today = date.today()
        with open(f"google_cache/{today}/{ticker}", "r") as f:
            data = json.load(f)
        return data

    def get_browser(self):
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        ]
        agent = random.choice(user_agents)
        return agent

    async def ai_crawler(self, link):
        agent = self.get_browser()
        
        async with AsyncWebCrawler(verbose=True,
            user_agent = agent,
            headers={"Accept-Language": "en-US"}, 
            sleep_on_close =False) as crawler:
            result = await crawler.arun(
                    url=link,        
                    magic=True)
            return result.markdown

    def process_news(self, news_item):

        """Accesses link from news_item and crawls it, retrieving article.
        Attaches article to news_item object. Returns news_item.
        """

        article = None
        if news_item["publisher"] == "MarketBeat":
            marketbeat = MarketBeat()
            article = marketbeat.extract_article(news_item["link"])
        else:
            article = asyncio.run(self.ai_crawler(news_item["link"]))
        
        
        if article == "\n":
            news_item["status"] = "WAITING_INDEX"
        elif article != "" and article != None:
            news_item["articles"] = [article]
            news_item["status"] = "INDEXED"
        else:
            news_item["status"] = "ERROR: ARTICLES NOT FOUND"

        return news_item
    
    def create_article(self, news_item):

        """Uploads article to MongoDB via an API."""

        api.api_entry = "http://dev.gputop.com/api"
        print(f"Creating article... -> {news_item['link']}")
        res = api.api_call("/news/create", data = news_item)

    def delete_articles(self):
        article_ids = ["CBMiswFBVV95cUxQS1JCaTNB…3a0lJNWlKMkhTTDIwZGhIMA",
        "CBMiywFBVV95cUxQRmFIZV9k…UJaU3lNbVlaRnFyeS1Sd0F0"
        ]
        api.api_entry = "https://headingtomars.com/api"
        for article_id in article_ids:
            print_b(" Delete news article " + article_id)
            json_res = api.api_call("/news/rm?id=" + article_id)
        #print_g(" Deletion was succesful ")

    def get_tickers(self):
        api_params = f"/index/batch/get_tickers"
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/ticker" + api_params)
        return data["tickers"]

    def pipeline(self):
        tickers = self.get_tickers()
        #for i in range(2):
        #    tickers.extend(self.get_tickers())
        for ticker in tickers:
            if ticker["exchange"] in ["NYSE", "NASDAQ"]:
                #self.discover_google_news(ticker["ticker"])
                google_news = self.read_from_cache(ticker["ticker"])
            
                for news_item in google_news:
                    news_item = self.process_news(news_item)
                    if news_item["status"] == "INDEXED" or news_item["STATUS"] == "WAITING_INDEX":
                        self.create_article(news_item)
                        print_g(f"ARTICLE CREATED: {news_item['publisher']}")
                    else:
                        print_r("ERROR: ARTICLE NOT FOUND")
        return

    def pipeline1(self):
        today = date.today()
        directory = f"google_cache/{today}"
        for ticker in os.listdir(directory):
            google_news = self.read_from_cache(ticker)
        
            for news_item in google_news:
                news_item = self.process_news(news_item)
                if news_item["status"] == "INDEXED" or news_item["STATUS"] == "WAITING_INDEX":
                    self.create_article(news_item)
                    print_g(f"ARTICLE CREATED: {news_item['publisher']}")
                else:
                    print_r("ERROR: ARTICLE NOT FOUND")
            return

    

gp = google_pipeline()
#gp.delete_articles()
gp.pipeline1()