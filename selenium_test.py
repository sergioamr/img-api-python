from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.binary_location = "./chrome/chrome/linux-128.0.6613.86/chrome-linux64/chrome"

service = ChromeService("./chrome/chromedriver-linux64/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.quit()
print("WebDriver initialized and quit successfully.")