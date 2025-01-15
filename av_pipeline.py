import random
import asyncio
from crawl4ai import AsyncWebCrawler
import os
from heapq import *
from datetime import date
import json

from imgapi.imgapi import ImgAPI
from colorama import Fore, Back, Style, init

from thelpers import *
from fetch.alpha_vantage.news_extractor_helpers import *
from fetch.alpha_vantage.download_news import *


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

class av_pipeline:
    def discover_news(self, ticker, api_key):

        """Finds news by stock ticker and sorts them by relevance."""

        news_arr = []
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&ticker={ticker}&apikey={api_key}"
        r = requests.get(url)
        data = r.json()
        
        for item in data["feed"]:
            if item["source"] in ["CNBC", "Money Morning", "Motley Fool", "South China Morning Post", "Zacks Commentary"]:
                if self.is_indexed(item):
                    continue
                relevance_score = get_relevance_score(item, ticker)
                if relevance_score > 0.20:
                    news_item = self.prepare_schema(item)
                    heappush(news_arr, (-relevance_score, news_item))
        self.cache_news(news_arr, ticker)
        return news_arr

    def is_indexed(self, item):

        """Using an API, checks if the news is in the database. Returns True if it is,
        False otherwise."""

        uuid = generate_uuid(item)
        api_params = f"?external_uuid={uuid}&source=ALPHAVANTAGE"
        api.api_entry = "http://dev.gputop.com/api"
        found = api.api_call("/news/query" + api_params)
        
        if len(found["news"]) > 0:
            return True    
        else:
            return False

    def prepare_schema(self, item):
        related_exchange_tickers = []
        for ticker in item["ticker_sentiment"]:
            if float(ticker["relevance_score"]) > 0.20:
                related_exchange_tickers.append(format_ticker(ticker["ticker"]))
        
        news_item = {
                "articles": [],
                "creation_date": parse_av_dates(item["time_published"]),
                "experiment": "ordersofmagnitude150125",
                "external_uuid": generate_uuid(item),
                "link": item["url"],
                "publisher": item["source"],
                "related_exchange_tickers": related_exchange_tickers,
                "source": "ALPHAVANTAGE",
                "status": "WAITING_INDEX",
            "title": item["title"]
            }
        return news_item

    def cache_news(self, news_arr, ticker):
        today = date.today()
        folder_path = os.path.join("av_cache", str(today))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        with open(f"av_cache/{today}/{ticker}", "w") as f:
            json.dump(news_arr, f, indent= 4)

    def read_from_cache(self, ticker):
        
        """Reads data from cache and returns"""

        today = date.today()
        with open(f"av_cache/{today}/{ticker}", "r") as f:
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
        article = None

        if news_item["publisher"] in ["CNBC", "Money Morning", "Motley Fool", "South China Morning Post"]:
            article = asyncio.run(self.ai_crawler(news_item["link"]))

        elif news_item["publisher"] == "Zacks Commentary":
            zacks = Zacks()
            article = zacks.extract_article(html)

        if article != None and article != "":
            news_item["articles"] = [article]
            news_item['status'] = "INDEXED"
        else:
            news_item['status'] = "ERROR: ARTICLES NOT FOUND"

        return news_item

    def get_tickers(self):
        api_params = f"/index/batch/get_tickers"
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/ticker" + api_params)
        return data["tickers"]

    def create_article(self, news_item):

        """Uploads article to MongoDB via an API."""

        api.api_entry = "http://dev.gputop.com/api"
        print(f"Creating article... -> {news_item['link']}")
        res = api.api_call("/news/create", data = news_item)

    

    def pipeline(self):
        processed = set()
        tickers = []

        for i in range(7):
            tickers.extend(self.get_tickers())

        #write code for API rotation - if data limit reached, go to next API
        api_keys = ["JIHXVRY5SPIH16C9", "H7YVHH7OWYL87Z8P", "USGT8VND71NUHLVN"]
        api_key = None
        i = 0

        for ticker in tickers:
            if ticker["exchange"] in ["NYSE", "NASDAQ"]:
                try:
                    api_key = api_keys[i]
                except KeyError:
                    break
                try:
                    av_news = self.discover_news(ticker["ticker"], api_key)                    
                except KeyError as e:
                    
                    print_r(f"Error {e}")
                    i += 1
                    continue

                #free API has request limits
                time.sleep(12)
                while av_news:
                    try:
                        relevance, news_item = heappop(av_news)
                    except TypeError:
                        relevance, news_item = random.choice(av_news)
                    
                    news_item = self.process_news(news_item)
                    if news_item["status"] == "INDEXED":
                        self.create_article(news_item)
                        print_g(f"ARTICLE CREATED: {news_item['publisher']}")
                    else:
                        print_r("ERROR: ARTICLE NOT FOUND")
        
        print_b(" FETCH FINISHED ")
