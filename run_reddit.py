import praw
import re
import os
import json
from datetime import datetime

from imgapi.imgapi import ImgAPI
from imgapi.tools import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

api = ImgAPI()

api.setup(config_file=".config.json")

DATA = "./DATA"
folders = [DATA]
for f in folders:
    ensure_dir(f)

##############################################################################################

reddit = praw.Reddit(
    client_id=api.reddit_id,
    client_secret=api.reddit_secret,
    user_agent="testscript by u/tothemoon_life",
)
print(reddit.auth.scopes())


def fetch_subreddit(subreddit_name):
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
    with open(f"{DATA}/{subreddit_name}_new_posts.json", "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)

    print(f"Downloaded {len(posts)} posts from r/{subreddit_name}!")


fetch_subreddit("Investing_AI")
fetch_subreddit("InvestingAI")

print_b(" FETCH FINISHED ")
