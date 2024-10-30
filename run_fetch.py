import re
import os
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
from selenium.webdriver.firefox.options import Options

init(autoreset=True)

api = ImgAPI()
api.setup("http://tothemoon.life/api", {})

json = api.api_call(
    "/news/query?status=WAITING_INDEX&limit=1&source=YFINANCE&publisher=GlobeNewswire"
)

print(Fore.BLUE + " FETCH " + str(json))


def get_webdriver():

    chrome_executable_path = "./chrome/chrome/linux-128.0.6613.86/chrome-linux64/chrome"
    chromedriver_path = "./chrome/chromedriver-linux64/chromedriver"

    # Check if Chrome executable exists
    if not os.path.exists(chrome_executable_path):
        raise FileNotFoundError(f"Chrome executable not found at {chrome_executable_path}")

    # Check if ChromeDriver exists
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}")

    # Step 1: Setup Chrome options
    chrome_options = Options()
    chrome_options.binary_location = chrome_executable_path  # Specify the location of the Chrome binary

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--window-size=1920,1200")

    # Step 2: Initialize the Chrome WebDriver

    # We have the driver in our system
    driver = webdriver.Chrome(service=ChromeService(chromedriver_path),
                              options=chrome_options)

    return driver


def print_b(text):
    print(Fore.BLUE + text)


def print_exception(err, text=''):
    import traceback
    print(Fore.RED + str(err))
    traceback.print_tb(err.__traceback__)


def clean_article(article):
    """Cleans \n character from article"""

    article = re.sub("\n", " ", article)
    return article


def get_IBD_articles(url, driver):
    "Use this for scraping news from investors.com"

    article = ""

    try:


        try:
            driver.get(url)

            current_url = driver.execute_script("return window.location.href;")
            print("Current URL:", current_url)

            if 'consent' in current_url:
                # We get the consent and click on it
                link = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "accept-all")))
                link.click()

        except Exception as e:
            pass

        try:
            current_url = driver.execute_script("return window.location.href;")
            print("Current URL:", current_url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "main")))

            print("Main Page Title:", driver.title)

            # Print all button elements on the main page
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(buttons)} buttons on the main page.")
            for index, button in enumerate(buttons):
                try:
                    if button.text:
                        print(f"Button {index + 1}:")
                        print("  Text:", button.text)
                        #print("  ID:", button.get_attribute("id"))
                        print("  Class:", button.get_attribute("class"))
                        #print("  Name:", button.get_attribute("name"))
                        print("  Type:", button.get_attribute("type"))
                except Exception as e:
                    print_exception(e, "CRASH")

            with open(
                    f"page_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    "w",
                    encoding="utf-8") as f:
                f.write(driver.page_source)

            link = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "readmore-button-class")))

            print(" LOADED BUTTON ")
            link.click()
        except Exception as e:
            print_exception(e, "CRASH")
            print(" Failed pressing button continue ")
            pass

        print(" LINK PRESSED ")
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for paragraph in paragraphs:
            if paragraph.text != "":
                article += paragraph.text
            if "YOU MIGHT ALSO LIKE" in paragraph.text:
                break
        article.replace("YOU MIGHT ALSO LIKE", "")

    except Exception as e:
        print_exception(e, "CRASH")

    driver.quit()
    return article


def yfetch_process_news(item):

    print_b("NEWS -> " + item['link'])

    driver = get_webdriver()

    articles = []

    print_b(" PUBLISHER " + item['publisher'])
    if item["publisher"] not in [
            "Barrons", "Financial Times", "The Information", "MT Newswires",
            "Investor's Business Daily", "Yahoo Finance Video"
    ]:
        driver.get(item["link"])

        try:
            # We get the consent
            link = driver.find_element(By.CLASS_NAME, "accept-all")
            link.click()
        except Exception as e:
            pass

        try:
            link = driver.find_element(By.CLASS_NAME, "readmoreButtonText")
            link.click()
        except Exception as e:
            print_exception(e, "CRASHED")
            pass

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
            if "title" in item:
                articles.append(item["title"])

        elif item["publisher"] == "Investor's Business Daily":
            try:
                article = get_IBD_articles(item["link"], driver)
                if article != "":
                    print_b(" OK ")
                    article = clean_article(article)
                    articles.append(article)
            except Exception as e:
                print_exception(e, " FAILED ")

    driver.quit()

    # Reindex because we haven't finish this code

    if len(articles) > 0:
        item.articles = articles
        item.save(validate=False)
        item.set_state("INDEXED")
    else:
        item.set_state("ERROR: ARTICLES NOT FOUND")


for article in json['news']:
    print(Fore.GREEN + " FETCH LINK " + article['link'])
    yfetch_process_news(article)

print(" TEST ")