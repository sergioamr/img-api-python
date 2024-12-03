import re
import os
import json
from datetime import datetime
from heapq import *
#from zenrows import ZenRowsClient

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

def get_webdriver():

    chrome_executable_path = "chrome/chrome/linux-128.0.6613.86/chrome-linux64/chrome"
    chromedriver_path = "chrome/chromedriver-linux64/chromedriver"

    '''# Check if Chrome executable exists
    if not os.path.exists(chrome_executable_path):
        raise FileNotFoundError(
            f"Chrome executable not found at {chrome_executable_path}")

    # Check if ChromeDriver exists
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(
            f"ChromeDriver not found at {chromedriver_path}")'''

    # Step 1: Setup Chrome options
    chrome_options = Options()
    chrome_options.binary_location = chrome_executable_path  # Specify the location of the Chrome binary

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1200")

    # Step 2: Initialize the Chrome WebDriver

    # We have the driver in our system
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_html(url):
    try:
        driver = get_webdriver()
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return [1, html]
    except Exception as e:
        print_r(f"Unable to extract html {url} because {e}")
        return [0, ""]

def extract_zenrows_html(url):

    client = ZenRowsClient("e8c73f9d4eaa246fec67e9b15bea42aad7aa09d0")
    try:
        response = client.get(url)
        html = response.text
    except Exception as e:
        print(e)
        return [0, ""]
    return [1, html]



###############################
def discover_google_news(ticker):
    
    google_publishers = ["24/7 Wall St.","Barchart", "Benzinga", "Fast Company", "Forbes", "ForexLive", "Fortune", "FXStreet",
                                "Insider Monkey", "Investing.com", "Investopedia", "Investor's Business Daily", "MarketBeat",
                                "Markets.com", "Marketscreener.com", "MoneyCheck", "Nasdaq", "Proactive Investors USA", "Reuters",
                                "StockTitan", "TipRanks", "TradingView", "Watcher Guru"]
    news = []
    gn = GoogleNews()

    #test the search function
    #company = get_company_name_from_ticker(ticker)
    search = gn.search(f"{ticker}")
    for item in search["entries"]:
        if item["source"]["title"] in google_publishers:
            news.append(item)
    return news

def google_process_news(api, item):

    """Function to extract and process google news based on website.
    Extract_html and extract_zenrows_html are in this file.
    The other helper functions are found in google/news_extractor_helpers.py
    """
    
    print_g("GOOGLE NEWS -> " + item["publisher"])
    print_g("GOOGLE NEWS -> " + item["link"])

    html = ""
    article = ""
    if item["publisher"] in ["Benzinga", "Reuters", "Investor's Business Daily"]:
        article = "This is a test article"

    elif item["publisher"] == "24/7 Wall St.":
        ws_247 = WS_247()
        success, html = extract_html(item["link"])
        article = ws_247.parse_article(html)
        to_process = True

    elif item["publisher"] == "Barchart":
        try:
            barchart = Barchart()
            success, html = barchart.extract_html(item["link"])
            article = barchart.parse_article(html)
        except Exception as e:
            print("Failed to extract Barchart")
            article = ""

    #elif item["publisher"] == "Benzinga":
    #    benzinga = Benzinga()
    #    success, html = extract_zenrows_html(item["link"])
    #    article = benzinga.extract_article(html)'''
    
    elif item["publisher"] == "Fast Company":
        fast_company = Fast_Company()
        success, html = extract_html(item["link"])
        article = fast_company.extract_article(html)
    
    elif item["publisher"] == "Forbes":
        success, html = extract_html(item["link"])
        print(html)
        forbes = Forbes()
        article = forbes.extract_article(html)
    
    elif item["publisher"] == "ForexLive":
        success, html = extract_html(item["link"])
        forex_live = Forex_Live()
        article = forex_live.extract_article(html)
    
    elif item["publisher"] == "Fortune":
        success, html = extract_html(item["link"])
        fortune = Fortune()
        article = fortune.extract_article(html)
    
    elif item["publisher"] == "FXStreet":
        success, html = extract_html(item["link"])
        fx_street = FX_Street()
        article = fx_street.extract_article(html)
    
    elif item["publisher"] == "Insider Monkey":
        insider_monkey = Insider_Monkey()
        success, html = extract_html(item["link"])
        article = insider_monkey.extract_article(html)
    
    elif item["publisher"] == "Investing.com":
        investing = Investing()
        success, html = extract_zenrows_html(item["link"])
        article = investing.extract_article(html)
    
    elif item["publisher"] == "InvestmentNews":
        investment_news = Investment_News()
        success, html = investment_news.extract_html(item["link"])
        article = investment_news.extract_article(html)
        
    elif item["publisher"] == "Investopedia":
        success, html = extract_html(item["link"])
        investopedia = Investopedia()
        article = investopedia.parse_article(html)
    
    #elif item["publisher"] == "Investor's Business Daily":
    #    ibd = IBD()
    #    success, html = extract_zenrows_html(item["link"])
    #    article = ibd.extract_article(html)
    
    elif item["publisher"] == "MarketBeat":
        marketbeat = Marketbeat()
        success, html = marketbeat.extract_html(item["link"])
        article = marketbeat.extract_article(html)
    
    elif item["publisher"] == "Markets.com":
        markets = Markets()
        success, html = markets.extract_html(item["link"])
        article = markets.extract_article(html)
    
    elif item["publisher"] == "Marketscreener.com":
        market_screener = Market_screener()
        success, html = extract_html(item["link"])
        article = market_screener.extract_article(html)
    
    elif item["publisher"] == "MoneyCheck":
        money_check = Money_Check()
        success, html = extract_html(item["link"])
        article = money_check.extract_article(html)
    
    elif item["publisher"] == "Nasdaq":
        nasdaq = NASDAQ()
        success, html = extract_html(item["link"])
        article = nasdaq.extract_article(html)
    
    elif item["publisher"] == "Proactive Investors USA":
        proactive_investors = Proactive_Investors()
        success, html = extract_html(item["link"])
        article = proactive_investors.extract_article(html)
    
    #elif item["publisher"] == "Reuters":
    #    reuters = Reuters()
    #    success, html = extract_zenrows_html(item["link"])
    #    article = reuters.extract_article(html)
    
    elif item["publisher"] == "TheStreet":
        the_street = The_Street()
        success, html = extract_html(item["link"])
        article = the_street.extract_article(html)
    
    elif item["publisher"] == "StockTitan":
        stock_titan = Stock_Titan()
        success, html = extract_html(item["link"])
        article = stock_titan.extract_article(html)
            
    elif item["publisher"] == "TipRanks":
        tipranks = TipRanks()
        success, html = tipranks.extract_html(item["link"])
        article = tipranks.parse_article(html, ticker)
    
    elif item["publisher"] == "Tokenist":
        tokenist = Tokenist()
        success, html = extract_html(item["link"])
        article = tokenist.extract_article(html, ticker)
    
    elif item["publisher"] == "TradingView":
        trading_view = Trading_View()
        success, html = extract_html(item["link"])
        article = trading_view.extract_article(html, ticker)
        
    elif item["publisher"] == "Watcher Guru":
        wg = WatcherGuru()
        success, html = extract_html(item["link"])
        article = wg.parse_article(html)
    
    print("html", html)
    print("article", article)
    item["experiment"] = "ordersofmagnitude"
    if article != "":
        item["articles"] = [article]
        item["status"] = "INDEXED"
    else:
        item["status"] = "ERROR: ARTICLES NOT FOUND"

    return item




def add_to_google_waiting_index(google_news):
    
    for news in google_news:
        external_uuid = news["id"]
        api_params = f"?external_uuid={external_uuid}&source=GOOGLE"
        found = api.api_call("/news/query" + api_params)
        
        #if article already in database, continue
        if len(found["news"]) > 0:
            continue

    
        article = {
                "articles": [],
                "creation_date": parse_google_dates(news["published"]),
                "experiment": "ordersofmagnitude",
                "external_uuid": news["id"],
                "link": news["link"],
                "publisher": news["source"]["title"],
                "source": "GOOGLE",
                "status": "WAITING_INDEX",
            "title": news["title"]
            }
        
        print("Creating article...", article)
        res = api.api_call("/news/create", data = article)
        

ticker = "NVDA"
google_news = discover_google_news(ticker)
add_to_google_waiting_index(google_news)

def delete_all_articles():
    api_params = "?source=GOOGLE&experiment=ordersofmagnitude"
    json_in = api.api_call("/news/query" + api_params)
    for article in json_in["news"]:
        print(article.keys())
        article_id = article["id"]
        print(article_id)
        json_res = api.api_call("/news/rm?id=" + article_id)


    #if not api.check_result(json_res, expected_state = "deleted"):
     #   exit()
    #print_json(json_res)
    print("Deletion was successful")


'''api_params = "?source=GOOGLE"
json_in = api.api_call("/news/query" + api_params)
print_b(f"json {json.dumps(json_in, indent=4)}")


for article in json_in['news']:
    article_id = article["id"]
    
    #article already in system
    if len(article["articles"]) > 0:
        continue
    
    print_b(" FETCH LINK " + article['link'])
    update = google_process_news(api, article)
    
    if update:
        # Api expects a list of news articles, we can batch later the calls
        js_dict = {'news': [update]}

        #fix update bugs
        res = api.api_call("/news/update", data=js_dict)
        print("res", res)
        if not res:
            print_e(" FAILED COMMUNICATING WITH API ")

        elif res["news"][0]['status'] == "ERROR: ARTICLES NOT FOUND":
            print_e(" API ERROR " + res['error_msg'])

        elif res["news"][0]['status'] != "INDEXED":
            print_r(json.dumps(res, indent=4))
            print_e(" FAILED UPDATING ")

        else:
            print_g(" UPDATE SUCCESSFUL ")

print_b("GOOGLE FETCH FINISHED ")'''
