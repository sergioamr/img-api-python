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



##############################################################################################
import praw

reddit = praw.Reddit(
    client_id=api.reddit_id,
    client_secret=api.reddit_secret,
    user_agent="testscript by u/tothemoon_life",
)
print(reddit.auth.scopes())

subreddit_name = "investing"
subreddit = reddit.subreddit(subreddit_name)

# Fetch the top posts
posts = []

# TOP
for submission in subreddit.new(limit=10):  # Adjust the limit as needed

    comment_list = []
    for comment in submission.comments:
        try:
            if comment.author:
                comment_list.append({
                    "body": comment.body,
                    "author": comment.author.name,
                    "created": comment.created,
                })
        except Exception as e:
            print_exception(e, "CRASHED")

    posts.append({
        "title": submission.title,
        "text": submission.selftext,
        "score": submission.score,
        "url": submission.url,
        "id": submission.id,
        "author": str(submission.author),
        "comments": submission.num_comments,
        "comment_list": comment_list
    })

import json
with open(f"{subreddit_name}_new_posts.json", "w", encoding="utf-8") as file:
    json.dump(posts, file, indent=4, ensure_ascii=False)

print(f"Downloaded {len(posts)} posts from r/{subreddit_name}!")

print_b(" FETCH FINISHED ")