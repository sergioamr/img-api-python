class MarketBeat:
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
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
    
        # Step 2: Initialize the Chrome WebDriver
    
        # We have the driver in our system
        driver = webdriver.Chrome(service=ChromeService(chromedriver_path),
                                  options=chrome_options)
        return driver


    def extract_html(self, link):
        driver = self.get_webdriver()
        driver.get(link)
        time.sleep(5)
        
        try:
            alert = driver.find_element(By.XPATH, "//button[contains(text(), 'Always Block')]").click()
            time.sleep(2)
            driver.switch_to.alert.dismiss()
        except Exception as e:
            print(e)
        
        try:
            notifications = driver.find_element(By.ID, "onesignal-slidedown-allow-button")
            driver.execute_script("arguments[0].click();", notifications)
        except Exception as e:
            print(e)
            pass
        
        driver.execute_script("window.scrollTo(0, 20)")
        
        try:
            signin_pop_up = driver.find_element(By.XPATH, "//button[@class = 'close2 bg-blue p-0']")
            signin_pop_up.click()
        except Exception as e:
            print(e)
            pass
        
        try:
            ads = driver.find_element(By.XPATH, "//div[@aria-label = 'Close ad']")
            time.sleep(2)
            ads.click()
        except Exception as e:
            print(e)
            pass
        
        html = driver.page_source
        driver.quit()
        return [1, html]
    
    def extract_article(self, link):
        success, html = self.extract_html(link)
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_= "body-copy lh-loose article-page")
        return article.get_text() 