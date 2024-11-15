import time
import re
import os
import logging as log
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from imgapi.imgapi import ImgAPI
from imgapi.scrapper import get_article
from imgapi.print_tools import *


DEFAULT_CHROME_PATH = "./chrome/chrome/linux-128.0.6613.86/chrome-linux64/chrome"
DEFAULT_CHROMEDRIVER_PATH = "./chrome/chromedriver-linux64/chromedriver"


def init(api):
    # Query NASDAQ companies
    api_params = "?exchanges=NASDAQ&limit=10&skip=0"

    json_in = api.api_call("/company/query" + api_params)
    log.debug(json.dumps(json_in, indent=4))

    companies = json_in["companies"]
    company = companies[0]
    symbol = get_ticker_symbol(company)

    driver = get_webdriver()
    news = get_news(driver, symbol)

    articles = []

    for link in news:
        if is_news(link):
            log.info("Link already exists")
            continue

        print(link)

        articles = [get_article(driver, link)]

        unixtime = time.mktime(datetime.now().timetuple())

        article = {
            'link': link,
            'title': "THIS IS A TEST",
            'external_uuid': "7bb12c17-a872-3080-ae2a-b56e967f2455",
            'publisher': "API_TEST",
            'articles': articles,
            'related_exchange_tickers': ["NASDAQ:TOTHEMOON", "NYE:GPUTOP"],
            'source': "IMG-API-PYTHON-API",
            'experiment': "img-api-demo-example",
            'creation_date': unixtime,
            'last_visited_date': unixtime,
            'status': "INDEXED",
        }

        res = api.api_call("/news/create", data=article)
        if api.check_result(res, expected_state="success"):
            delete_article(res)
            print_json(res)
            print_g("================================= ")
            print_g(" FETCH FINISHED ")
        else:
            print_e(" FETCH FINISHED WITH ERRORS ")

        break

    driver.close()

def delete_article(article):
    """ Example of how to delete an article
    """
    article_id = article['news'][0]['id']

    print_b(" Delete news article " + article_id)
    json_res = api.api_call("/news/rm?id=" + article_id, test=True)

    # Check if the API was successful, API will return state="deleted" if successful
    if not api.check_result(json_res, expected_state="deleted"):
        exit()

    print_json(json_res)
    print_g(" Deletion was succesful ")


def clean_article(article):
    """Cleans \n character from article"""

    article = re.sub("\n", " ", article)
    return article


def is_news(link):
    api_params = f"?link__icontains={link}"
    json_in = api.api_call("/news/query" + api_params)
    return bool(json_in["news"])


def get_news(driver, symbol):
    news = []
    url = f"https://stocktwits.com/symbol/{symbol}/news"

    driver.get(url)

    anchors = driver.find_elements(By.TAG_NAME, "a")

    for index, anchor in enumerate(anchors):
        href = anchor.get_attribute("href")
        if not href or "stocktwits" in href:
            continue

        news.append(href)

    return news


def get_ticker_symbol(company):
    exchange_ticker = company["exchange_tickers"][0]
    symbol_pattern = r':(.+)'
    symbol = re.search(symbol_pattern, exchange_ticker).group(1)
    log.debug(f"Symbol: {symbol}")
    return symbol


def get_webdriver():
    chrome_executable_path = os.environ.get("DEFAULT_CHROME_PATH", DEFAULT_CHROME_PATH)
    chromedriver_path = os.environ.get("DEFAULT_CHROMEDRIVER_PATH", DEFAULT_CHROMEDRIVER_PATH)

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


if __name__ == "__main__":
    api = ImgAPI()

    api.setup(config_file=".config.json")

    init(api)