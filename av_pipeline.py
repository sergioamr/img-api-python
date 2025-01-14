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
    def discover_av_news(self, ticker, api_key):

        """Finds news by stock ticker and sorts them by relevance."""

        news = []
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&ticker={ticker}&apikey={api_key}"
        r = requests.get(url)
        data = r.json()
        #print(data)
        
        for news_item in data["feed"]:
            if news_item["source"] in ["CNBC", "Money Morning", "Motley Fool", "South China Morning Post", "Zacks Commentary"]:
                relevance_score = get_relevance_score(news_item, ticker)
                if relevance_score > 0.20:
                    print(news, -relevance_score, news_item)
                    heappush(news, (-relevance_score, news_item))
        today = date.today()
        folder_path = os.path.join("cache", str(today))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        with open(f"cache/{today}/{ticker}", "w") as f:
            json.dump(news, f, indent= 4)
        return news

    def in_database(self, item, uuid):
        """Checks if news is already in database. Returns True if in database,
        False otherwise."""

        api_params = f"?external_uuid={uuid}&source=ALPHAVANTAGE"
        api.api_entry = "http://dev.gputop.com/api"
        found = api.api_call("/news/query" + api_params)
        
        #if article already in database, continue
        if len(found["news"]) > 0:
            return True    
        else:
            return False

    def add_to_waiting_index(self, item, uuid):

        """Takes a news item, prepares its data schema, and adds it to the database."""

        print_g(f"Currently adding to database -> {item}")

        related_exchange_tickers = []
        for ticker in item["ticker_sentiment"]:
            if float(ticker["relevance_score"]) > 0.29:
                related_exchange_tickers.append(format_ticker(ticker["ticker"]))
        
        article = {
                "articles": [],
                "creation_date": parse_av_dates(item["time_published"]),
                "external_uuid": uuid,
                "link": item["url"],
                "publisher": item["source"],
                "related_exchange_tickers": related_exchange_tickers,
                "source": "ALPHAVANTAGE",
                "status": "WAITING_INDEX",
            "title": item["title"]
            }
        
        api.api_entry = "http://dev.gputop.com/api"
        res = api.api_call("/news/create", data = article)
        print_g(f"News uploaded, {res}")
        return article



    def process_news(self, api, item):

        """Function to process news based on website. Subfunctions6 are in fetch/alpha_vantage/news_extractor_helpers.py.
        """

        print_g("AV NEWS /c -> " + item["link"])
        article = ""

        fetch = News_Fetch_Helpers()
        if item["publisher"] == "CNBC":
            success, html = fetch.extract_html(item["link"])
            cnbc = CNBC()
            article = cnbc.extract_article(html)

        elif item["publisher"] == "Money Morning":
            success, html = fetch.extract_html(item["link"])
            money_morning = Money_Morning()
            article = money_morning.extract_article(html)

        elif item["publisher"] == "Motley Fool":
            success, article = fetch.extract_html(item["link"])
            motley = Motley()
            article = motley.parse_motley(article)

        elif item["publisher"]  == "South China Morning Post":
            success, html = fetch.extract_html(item["link"])
            scmp = SCMP()
            article = scmp.extract_article(html)

        elif item["publisher"] == "Zacks Commentary":
            zacks = Zacks()
            success, html = zacks.extract_html(item["link"])
            article = zacks.extract_article(html)

        if article != "":
            item["articles"] = [article]
            item['status'] = "INDEXED"
        else:
            item['status'] = "ERROR: ARTICLES NOT FOUND"

        return item

    def pipeline_test(self):
        #how do you store the api_keys so that it's not on github?
        api_keys = ["JIHXVRY5SPIH16C9", "H7YVHH7OWYL87Z8P"]
        api_params = f"/index/batch/get_tickers"
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/ticker" + api_params)
        tickers = data["tickers"]
        i = 0
        api_key = None
        not_found = []

        for ticker in tickers:
            print_g(f"Currently processing... {i}, {ticker['ticker']}, {ticker['exchange']}")        
            if ticker["exchange"] in ["NYSE", "NASDAQ"]:
                i += 1
                try:
                    av_news = self.discover_av_news(ticker["ticker"], api_key)
                except Exception as e:
                    print_r(f"Error {e}")
                    print_r(f"{ticker['ticker']} not found")
                    not_found.append(ticker["ticker"])
                    continue
                while av_news:
                    try:
                        relevance, item = heappop(av_news)
                    except TypeError:
                        relevance, item = random.choice(av_news)
                    
                    #generate uuid
                    uuid = generate_uuid(item)
                    if self.in_database(item, uuid):
                        print_r("News already in database...")
                        continue
                    else:
                        item = self.add_to_waiting_index(item, uuid)
                        update = self.process_news(api, item)
                        if update:
                            js_dict = {'news': [update]}

                            print(json.dumps(js_dict, indent=4))
                            api.api_entry = "http://dev.gputop.com/api"
                            res = api.api_call("/news/update", data=js_dict)

                            if not res:
                                print_e(" FAILED COMMUNICATING WITH API ")

                            elif res['status'] == "error":
                                print_e(" API ERROR " + res['error_msg'])

                            elif res['status'] != "success":
                                print_r(json.dumps(res, indent=4))
                                print_e(" FAILED UPDATING ")

                            else:
                                print_g(" UPDATE SUCCESSFUL ")

        print_b(" FETCH FINISHED ")
        return not_found

            
                
                
    
    

avp = av_pipeline()
avp.pipeline_test()

