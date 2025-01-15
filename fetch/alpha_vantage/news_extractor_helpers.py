class Zacks:
    def get_webdriver(self):
    
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
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
        # Step 2: Initialize the Chrome WebDriver
    
        # We have the driver in our system
        driver = webdriver.Chrome(service=ChromeService(chromedriver_path),
                                  options=chrome_options)
        return driver

    def extract_html(self, link):
        driver = self.get_webdriver()
        try:
            driver.get(link)
            element = EC.presence_of_element_located(
                (By.CLASS_NAME, "show_article"))

            WebDriverWait(driver, 3).until(element)
            driver.execute_script("arguments[0].scrollIntoView();", element)
            timer = random.uniform(0.5, 1)
            time.sleep(timer)
            element.click()
        except Exception as e:
            print("Error extracting news", e)
            return [0, ""]
        finally:
            html = driver.page_source
            driver.close()
            return [1, html]

    def extract_article(self, link):
        success, html = self.extract_html(link)
        soup = BeautifulSoup(html, "html.parser")
        raw_articles = soup.find_all("article")
        article = ""
        for raw_article in raw_articles:
            article += raw_article.get_text()
        return article