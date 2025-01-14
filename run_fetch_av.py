import re
import os
import json
from datetime import datetime
from heapq import *

from urllib.parse import quote_plus
from imgapi.imgapi import ImgAPI
#from imgapi.print_tools import *
from colorama import Fore, Back, Style, init

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from thelpers import *
from fetch.alpha_vantage.news_extractor_helpers import *
from fetch.alpha_vantage.download_news import *
from fetch.google.download_news import *
from fetch.google.news_extractor_helpers import *

init(autoreset=True)

api = ImgAPI()
api.setup(config_file="config.json")

def download_av_news(ticker, db_ticker = False):
    if db_ticker:
        ticker = db_ticker.ticker
        exchange = db_ticker.symbol
        if exchange in ["NYSE", "NASDAQ", "NYQ", "NYE"]:
            av_news = get_usa_news(ticker)
    else:
        av_news = get_usa_news(ticker)
    return av_news

def delete_article(article):
    """ Example of how to delete an article
    """
    article_id = article['news'][0]['id']

    print(" Delete news article " + article_id)
    json_res = api.api_call("/news/rm?id=" + article_id)

    # Check if the API was successful, API will return state="deleted" if successful
    if not api.ch5eck_result(json_res, expected_state="deleted"):
        exit()

    print(json_res)
    print(" Deletion was succesful ")


api = ImgAPI()

api.setup(config_file="config.json")

# Search first for our Test article to see if it is already indexed

test_url = "https://linkslog.org"
api_params = "link=" + quote_plus(test_url)

json_in = api.api_call("/news/query?" + api_params)
if not json_in:
    exit()

print(json_in)

# If there is an article with this link, delete it

if len(json_in['news']) > 0:
    print("THERE ARE ALREADY NEWS ON THE SYSTEM WITH THIS LINK")
    delete_article(json_in)

# Dummy article to upload

unixtime = time.mktime(datetime.datetime.now().timetuple())

article = {
    'link': test_url,
    'title': "THIS IS A TEST",
}

# Call to create and upload a new article.
res = api.api_call("/news/create", data=article)

if api.check_result(res, expected_state="success"):
    delete_article(res)
    print(res)
    print("================================= ")
    print(" FETCH FINISHED ")
else:
    print(" FETCH FINISHED WITH ERRORS ")

