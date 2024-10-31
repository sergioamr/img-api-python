import re
import os
import json
from datetime import datetime

from imgapi.imgapi import ImgAPI
from colorama import Fore, Back, Style, init

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from alpha_vantage import *
from google import *

init(autoreset=True)

api = ImgAPI()

api.setup(config_file=".config.json")


def get_webdriver():

    chrome_executable_path = "./chrome/chrome/linux-128.0.6613.86/chrome-linux64/chrome"
    chromedriver_path = "./chrome/chromedriver-linux64/chromedriver"

    # Check if Chrome executable exists
    if not os.path.exists(chrome_executable_path):
        raise FileNotFoundError(
            f"Chrome executable not found at {chrome_executable_path}")

    # Check if ChromeDriver exists
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(
            f"ChromeDriver not found at {chromedriver_path}")

    # Step 1: Setup Chrome options
    chrome_options = Options()
    chrome_options.binary_location = chrome_executable_path  # Specify the location of the Chrome binary

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1200")

    # Step 2: Initialize the Chrome WebDriver

    # We have the driver in our system
    driver = webdriver.Chrome(service=ChromeService(chromedriver_path),
                              options=chrome_options)

    return driver


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


def clean_article(article):
    """Cleans \n character from article"""

    article = re.sub("\n", " ", article)
    return article


def yfetch_process_news(api, item):

    print_g(" NEWS -> " + item['link'])

    driver = get_webdriver()

    articles = []

    print_b(" PUBLISHER " + item['publisher'])
    if item["publisher"] not in [
            "Barrons", "Financial Times", "The Information", "MT Newswires",
            "Investor's Business Daily", "Yahoo Finance Video"
    ]:
        driver.get(item["link"])

        try:
            # Check first if we are in the consent page (EU)
            current_url = driver.execute_script("return window.location.href;")

            if 'consent' in current_url:
                print(" CONSENT URL:", current_url)
                # We get the consent and click on it

                accept_element = EC.element_to_be_clickable(
                    (By.CLASS_NAME, "accept-all"))

                link = WebDriverWait(driver, 5).until(accept_element)
                link.click()

        except Exception as e:
            print_exception(e, "CRASHED READING CONSENT")
            pass

        try:
            current_url = driver.execute_script("return window.location.href;")
            print(" URL:", current_url)

            element_present = EC.presence_of_element_located(
                (By.TAG_NAME, 'main'))

            WebDriverWait(driver, 5).until(element_present)

            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(buttons)} buttons on the main page.")
            for index, button in enumerate(buttons):
                try:
                    if not button.text: continue
                    if button.get_attribute("type") == "submit": continue

                    cl = button.get_attribute("class")
                    print(
                        f"Button {index + 1} Text: {Fore.BLUE} {button.text} {Style.RESET_ALL} {cl} "
                    )
                except Exception as e:
                    print_exception(e, "CRASH")

            try:
                link = driver.find_element(By.CLASS_NAME, "readmoreButtonText")
                if link:
                    link.click()
            except Exception as e:
                print_r(" NO READ MORE BUTTON ")

        except Exception as e:
            print_exception(e, "CRASHED")

        try:
            article = driver.find_element(By.TAG_NAME, "article")
            article = article.text

        except:
            print("article tag not found", item["publisher"])
            article = ""
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for paragraph in paragraphs:
                article += paragraph.text
            article = clean_article(article)
        finally:
            articles.append(article)

        driver.close()
    else:
        if item["publisher"] in ["Barrons", "MT Newswires"]:
            print_e(" TO BE IMPLEMENTED ")

        elif item["publisher"] == "Investor's Business Daily":
            try:
                print_e(" TO BE IMPLEMENTED ")
            except Exception as e:
                print_exception(e, " FAILED ")

    driver.quit()

    # Reindex because we haven't finish this code

    if len(articles) > 0:
        item['articles'] = articles
        item['state'] = "INDEXED"
    else:
        item['state'] = "ERROR: ARTICLES NOT FOUND"

    return item


def av_process_news(api, item):
    print_b("NEWS -> " + item["link"])

    data_folder = item.get_data_folder()
    print_b("DATA FOLDER: " + data_folder)
    article = ""
    #where do i put the code for downloading & discovery?
    #code in alphavantage/helpers.py
    if item["publisher"] == "CNBC":
        success, html = extract_html(item["url"])
        cnbc = CNBC()
        article = cnbc.extract_article(html)

    elif item["publisher"] == "Money Morning":
        success, html = extract_html(item["url"])
        money_morning = Money_Morning()
        article = money_morning.extract_article(html)

    elif item["publisher"] == "Motley Fool":
        success, article = extract_html(item["url"])
        motley = Motley()
        article = motley.parse_motley(article)

    elif item["publisher"]  == "South China Morning Post":
        success, html = extract_html(news["url"])
        scmp = SCMP()
        article = scmp.extract_article(html)

    elif item["publisher"] == "Zacks Commentary":
        success, html = extract_zacks_html(news["url"])
        zacks = Zacks()
        article = zacks.extract_article(html)

    if article != "":
        item['articles'] = articles
        item['state'] = "INDEXED"
    else:
        item['state'] = "ERROR: ARTICLES NOT FOUND"

    return item

def google_process_news(api, item):
    print("Currently extracting", result["source"]["title"])
    print(result["link"])
    article = ""
    if item["publisher"] == "24/7 Wall St.":
        ws_247 = WS_247()
        success, html = extract_html(result["link"])
        article = ws_247.parse_article(html)
        to_process = True

    elif item["publisher"] == "Barchart":
        try:
            barchart = Barchart()
            success, html = barchart.extract_html(result["link"])
            article = barchart.parse_article(html)
        except Exception as e:
            print("Failed to extract Barchart")
            article = ""

    elif item["publisher"] == "Benzinga":
        benzinga = Benzinga()
        success, html = extract_zenrows_html(result["link"])
        article = benzinga.extract_article(html)
    
    elif item["publisher"] == "Fast Company":
        fast_company = Fast_Company()
        success, html = extract_html(result["link"])
        article = fast_company.extract_article(html)
    
    elif item["publisher"] == "Forbes":
        success, html = extract_html(result["link"])
        forbes = Forbes()
        article = forbes.extract_article(html)
    
    elif item["publisher"] == "ForexLive":
        success, html = extract_html(result["link"])
        forex_live = Forex_Live()
        article = forex_live.extract_article(html)
    
    elif item["publisher"] == "Fortune":
        success, html = extract_html(result["link"])
        fortune = Fortune()
        article = fortune.extract_article(html)
    
    elif item["publisher"] == "FXStreet":
        success, html = extract_html(result["link"])
        fx_street = FX_Street()
        article = fx_street.extract_article(html)
    
    elif item["publisher"] == "Insider Monkey":
        insider_monkey = Insider_Monkey()
        success, html = extract_html(result["link"])
        article = insider_monkey.extract_article(html)
    
    elif item["publisher"] == "Investing.com":
        investing = Investing()
        success, html = extract_zenrows_html(result["link"])
        article = investing.extract_article(html)
    
    elif item["publisher"] == "InvestmentNews":
        investment_news = Investment_News()
        success, html = investment_news.extract_html(result["link"])
        article = investment_news.extract_article(html)
        
    elif item["publisher"] == "Investopedia":
        success, html = extract_html(result["link"])
        investopedia = Investopedia()
        article = investopedia.parse_article(html)
    
    elif item["publisher"] == "Investor's Business Daily":
        ibd = IBD()
        success, html = extract_zenrows_html(result["link"])
        article = ibd.extract_article(html)
    
    elif item["publisher"] == "MarketBeat":
        marketbeat = Marketbeat()
        success, html = marketbeat.extract_html(result["link"])
        article = marketbeat.extract_article(html)
    
    elif item["publisher"] == "Markets.com":
        markets = Markets()
        success, html = markets.extract_html(result["link"])
        article = markets.extract_article(html)
    
    elif item["publisher"] == "Marketscreener.com":
        market_screener = Market_screener()
        success, html = extract_html(result["link"])
        article = market_screener.extract_article(html)
    
    elif item["publisher"] == "MoneyCheck":
        money_check = Money_Check()
        success, html = extract_html(result["link"])
        article = money_check.extract_article(html)
    
    elif item["publisher"] == "Nasdaq":
        nasdaq = NASDAQ()
        success, html = extract_html(result["link"])
        article = nasdaq.extract_article(html)
    
    elif item["publisher"] == "Proactive Investors USA":
        proactive_investors = Proactive_Investors()
        success, html = extract_html(result["link"])
        article = proactive_investors.extract_article(html)
    
    elif item["publisher"] == "Reuters":
        reuters = Reuters()
        success, html = extract_html(result["link"])
        article = reuters.extract_article(html)
    
    elif item["publisher"] == "TheStreet":
        the_street = The_Street()
        success, html = extract_html(result["link"])
        article = the_street.extract_article(html)
    
    elif item["publisher"] == "StockTitan":
        stock_titan = Stock_Titan()
        success, html = extract_html(result["link"])
        article = stock_titan.extract_article(html)
            
    elif item["publisher"] == "TipRanks":
        tipranks = TipRanks()
        success, html = tipranks.extract_html(result["link"])
        article = tipranks.parse_article(html, ticker)
    
    elif item["publisher"] == "TradingView":
        tokenist = Tokenist()
        success, html = extract_html(result["link"])
        article = tokenist.extract_article(html, ticker)
    
    elif item["publisher"] == "TradingView":
        trading_view = Trading_View()
        success, html = extract_html(result["link"])
        article = trading_view.extract_article(html, ticker)
        
    elif item["publisher"] == "Watcher Guru":
        wg = WatcherGuru()
        success, html = extract_html(result["link"])
        article = wg.parse_article(html)

    if len(articles) > 0:
        item['articles'] = article
        item['state'] = "INDEXED"
    else:
        item['state'] = "ERROR: ARTICLES NOT FOUND"

    return item



##############################################################################################

api_params = "?status=WAITING_INDEX&limit=1&source=YFINANCE&publisher=GlobeNewswire"

json_in = api.api_call("/news/query" + api_params)
print_b(json.dumps(json_in, indent=4))

for article in json_in['news']:
    print_b(" FETCH LINK " + article['link'])
    update = yfetch_process_news(api, article)

    if update:
        # Api expects a list of news articles, we can batch later the calls
        js_dict = {'news': [update]}

        print(json.dumps(js_dict, indent=4))
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