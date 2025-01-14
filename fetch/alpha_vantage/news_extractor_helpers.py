from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import re
import time
import os

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


def remove_word(word, article):

    """Takes in article string as input, removes all instances of unwanted word from it"""

    article = re.sub(word, " ", article)
    return article


class CNBC:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_articles = soup.find_all("div", class_="group")
        article = []
        for raw_article in raw_articles:
            article.append(raw_article.get_text()+"\n")
        article = "\n".join(article)
        article = remove_word("\xa0", article)
        article = self.clean_links(html, article)
        return article

    def clean_links(self, html, article):
        soup = BeautifulSoup(html, "html.parser")
        to_remove = []
        related_content = soup.find("div", class_ = "RelatedContent-container")
        if related_content == None:
            return article
        rc = related_content.find_all("li")
        for c in rc:
            to_remove.append(c.get_text())

        for sentence in to_remove:
            article = remove_word(sentence, article)
        return article

class Money_Morning:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_article = soup.find("div", class_ = "single-content").get_text()
        return raw_article

class Motley:
    def get_motley_sales_pitch(self, soup):
        sales_pitch = soup.find(class_ = "article-pitch-container")
        if sales_pitch == None:
            return ""
        else:
            return sales_pitch.get_text()

    def get_motley_captions(self, soup):
        raw_captions = soup.find_all(class_ = "caption")
        captions = []
        for caption in raw_captions:
            captions.append(caption.get_text())
        return captions

    def get_motley_imgs(self, soup):
        imgs = ""
        raw_imgs = soup.find_all(class_ = "company-card-vue-component")
        for img in raw_imgs:
            imgs += img.get_text()
        return imgs.split("\n")


    def parse_motley(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_article = soup.find_all(class_ = "article-body")
        raw_article = raw_article[0].get_text()
        raw_article_split = raw_article.split("\n")

        sales_pitch = self.get_motley_sales_pitch(soup)
        captions = self.get_motley_captions(soup)
        imgs = self.get_motley_imgs(soup)

        article = []

        for paragraph in raw_article_split:
            if paragraph == "":
                continue

            if paragraph in sales_pitch:
                continue

            if paragraph in captions:
                continue

            if paragraph in imgs:
                continue

            if "Arrows-In" in paragraph:
                continue

            if "Key Data Points" in paragraph:
                continue

            article.append(paragraph+"\n")

        return "\n".join(article)

class SCMP:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article").get_text()
        return article

class Zacks:
    def extract_html(self, link):
        driver = get_webdriver()
        try:
            driver.get(link)
            element = EC.presence_of_element_located(
                (By.CLASS_NAME, "show_article"))

            WebDriverWait(driver, 5).until(element)
            element.click()
        except Exception as e:
            print("Error extracting news", e)
            return [0, ""]
        finally:
            html = driver.page_source
            driver.close()
            return [1, html]

    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_articles = soup.find_all("article")
        article = ""
        for raw_article in raw_articles:
            article += raw_article.get_text()
        return article