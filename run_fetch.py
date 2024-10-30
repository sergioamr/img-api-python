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