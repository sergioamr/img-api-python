import re
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



nfp = News_Fetch_Helpers()
class Google_pipeline:
    def discover_google_news(self, ticker):
        
        news = []
        gn = GoogleNews()

        #test the search function
        company = get_company_name_from_ticker(ticker)
        search = gn.search(f"{company}")
        for item in search["entries"]:

            #exclude Yahoo and AlphaVantage publishers
            if item["source"]["title"] in ["Forbes", "ForexLive", "Fortune", "MarketBeat", "Simply Wall St", "StockTitan"]:
                news.append(item)
        return news

    def is_indexed(self, item):
        external_uuid = item["id"]
        api_params = f"?external_uuid={external_uuid}&source=GOOGLE"
        api.api_entry = "http://dev.gputop.com/api"
        found = api.api_call("/news/query" + api_params)
        
        #if article already in database, continue
        if len(found["news"]) > 0:
            print_r(f"News already in database!")
            return True
        else:
            return False

    def prepare_schema(self, item):
        link = new_decoderv1(item["link"])
        news_item = {
                "articles": [],
                "creation_date": parse_google_dates(item["published"]),
                "experiment": "ordersofmagnitude",
                "external_uuid": item["id"],
                "link": link["decoded_url"],
                "publisher": item["source"]["title"],
                "source": "GOOGLE",
                "status": "WAITING_INDEX",
            "title": item["title"]
            }
        return news_item

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
    

    async def ai_crawler(self, link, html = False):
        agent = self.get_browser()
        async with AsyncWebCrawler(verbose=True, user_agent = agent,
            headers={"Accept-Language": "en-US"}, 
            sleep_on_close =False) as crawler:
            result = await crawler.arun(
                    url=link,        
                    magic=True)
            if html == True:
                return result.html
            else:
                return result.markdown

    def process_news(self, item):
        """Function to extract and process google news based on website.
            Extract_html and extract_zenrows_html are in this file.
            The other helper functions are found in google/news_extractor_helpers.py
        """
        news_item = self.prepare_schema(item)
        article = None

        if news_item["publisher"] == "MarketBeat":
            marketbeat = Marketbeat()
            success, html = marketbeat.extract_html(item["link"])
            article = marketbeat.extract_article(html)
        
        #simply wall street2
        elif news_item["publisher"] in ["Forbes", "ForexLive", "Fortune", "Investor's Business Daily", "Investopedia", "Investing.com", "Simply Wall St", "StockTitan"]:
            article = asyncio.run(self.ai_crawler(item["link"]))

        if article != None:
            news_item["articles"] = [article]
            news_item["status"] = "INDEXED"
            api.api_entry = "http://dev.gputop.com/api"
            #print(article)
            print_b(f"Creating article... -> {news_item['publisher']}")
            res = api.api_call("/news/create", data = news_item)
            
        else:
            news_item["status"] = "ERROR: ARTICLES NOT FOUND"

        return news_item

    def delete_news(self, query):
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/news/query" + query)
        for item in data["news"]:
            article_id = item["id"]
            print_b(" Delete news article " + article_id)
            json_res = api.api_call("/news/rm?id=" + article_id)

    def delete_all_articles(self):
        api_params = f"?experiment=ordersofmagnitude&source=GOOGLE"
        api.api_entry = "http://dev.gputop.com/api"
        data = api.api_call("/news/query" + api_params)
        for item in data["news"]:
            article_id = item["id"]
            print_b(" Delete news article " + article_id)
            json_res = api.api_call("/news/rm?id=" + article_id)

        print_g(" Deletion was succesful ")


    def pipeline_test(self):
        api_params = f"/index/batch/get_tickers"
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/ticker" + api_params)
        tickers = data["tickers"]
        for ticker in tickers:
            google_news = self.discover_google_news(ticker["ticker"])
        
            for item in google_news:   
                if self.is_indexed(item):
                    continue
                else:
                    update = self.process_news(item)
                    if update["articles"] != []:
                        print_g(" UPDATE SUCCESSFUL ")
                    else:
                        print_e(" FAILED UPDATING ")
                            
        print_b(" FETCH FINISHED ")

gp = Google_pipeline()
#gp.delete_all_articles()
gp.pipeline_test()