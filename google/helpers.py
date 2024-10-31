
class GoogleNews:
    """Code for news discovery and parsing newsfeed"""

    def __init__(self, lang = 'en', country = 'US'):
        self.lang = lang.lower()
        self.country = country.upper()
        self.BASE_URL = 'https://news.google.com/rss'

    def __top_news_parser(self, text):
        """Return subarticles from the main and topic feeds"""
        try:
            bs4_html = BeautifulSoup(text, "html.parser")
            # find all li tags
            lis = bs4_html.find_all('li')
            sub_articles = []
            for li in lis:
                try:
                    sub_articles.append({"url": li.a['href'],
                                         "title": li.a.text,
                                         "publisher": li.font.text})
                except:
                    pass
            return sub_articles
        except:
            return text

    def __ceid(self):
        """Compile correct country-lang parameters for Google News RSS URL"""
        return '?ceid={}:{}&hl={}&gl={}'.format(self.country,self.lang,self.lang,self.country)

    def __add_sub_articles(self, entries):
        for i, val in enumerate(entries):
            if 'summary' in entries[i].keys():
                entries[i]['sub_articles'] = self.__top_news_parser(entries[i]['summary'])
            else:
                entries[i]['sub_articles'] = None
        return entries

    def __scaping_bee_request(self, api_key, url):
        response = requests.get(
            url="https://app.scrapingbee.com/api/v1/",
            params={
                "api_key": api_key,
                "url": url,
                "render_js": "false"
            }
        )
        if response.status_code == 200:
            return response
        if response.status_code != 200:
            raise Exception("ScrapingBee status_code: "  + str(response.status_code) + " " + response.text)

    def __parse_feed(self, feed_url, proxies=None, scraping_bee = None):

        if scraping_bee and proxies:
            raise Exception("Pick either ScrapingBee or proxies. Not both!")

        if proxies:
            r = requests.get(feed_url, proxies = proxies)
        else:
            r = requests.get(feed_url)

        if scraping_bee:
            r = self.__scaping_bee_request(url = feed_url, api_key = scraping_bee)
        else:
            r = requests.get(feed_url)


        if 'https://news.google.com/rss/unsupported' in r.url:
            raise Exception('This feed is not available')

        d = feedparser.parse(r.text)

        if not scraping_bee and not proxies and len(d['entries']) == 0:
            d = feedparser.parse(feed_url)

        return dict((k, d[k]) for k in ('feed', 'entries'))

    def __search_helper(self, query):
        return urllib.parse.quote_plus(query)

    def __from_to_helper(self, validate=None):
        try:
            validate = parse_date(validate).strftime('%Y-%m-%d')
            return str(validate)
        except:
            raise Exception('Could not parse your date')



    def top_news(self, proxies=None, scraping_bee = None):
        """Return a list of all articles from the main page of Google News
        given a country and a language"""
        d = self.__parse_feed(self.BASE_URL + self.__ceid(), proxies=proxies, scraping_bee=scraping_bee)
        d['entries'] = self.__add_sub_articles(d['entries'])
        return d

    def topic_headlines(self, topic: str, proxies=None, scraping_bee=None):
        """Return a list of all articles from the topic page of Google News
        given a country and a language"""
        #topic = topic.upper()
        if topic.upper() in ['WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SCIENCE', 'SPORTS', 'HEALTH']:
            d = self.__parse_feed(self.BASE_URL + '/headlines/section/topic/{}'.format(topic.upper()) + self.__ceid(), proxies = proxies, scraping_bee=scraping_bee)

        else:
            d = self.__parse_feed(self.BASE_URL + '/topics/{}'.format(topic) + self.__ceid(), proxies = proxies, scraping_bee=scraping_bee)

        d['entries'] = self.__add_sub_articles(d['entries'])
        if len(d['entries']) > 0:
            return d
        else:
            raise Exception('unsupported topic')

    def geo_headlines(self, geo: str, proxies=None, scraping_bee=None):
        """Return a list of all articles about a specific geolocation
        given a country and a language"""
        d = self.__parse_feed(self.BASE_URL + '/headlines/section/geo/{}'.format(geo) + self.__ceid(), proxies = proxies, scraping_bee=scraping_bee)

        d['entries'] = self.__add_sub_articles(d['entries'])
        return d

    def search(self, query: str, helper = True, when = None, from_ = None, to_ = None, proxies=None, scraping_bee=None):
        """
        Return a list of all articles given a full-text search parameter,
        a country and a language

        :param bool helper: When True helps with URL quoting
        :param str when: Sets a time range for the artiles that can be found
        """

        if when:
            query += ' when:' + when

        if from_ and not when:
            from_ = self.__from_to_helper(validate=from_)
            query += ' after:' + from_

        if to_ and not when:
            to_ = self.__from_to_helper(validate=to_)
            query += ' before:' + to_

        if helper == True:
            query = self.__search_helper(query)

        search_ceid = self.__ceid()
        search_ceid = search_ceid.replace('?', '&')

        d = self.__parse_feed(self.BASE_URL + '/search?q={}'.format(query) + search_ceid, proxies = proxies, scraping_bee=scraping_bee)

        d['entries'] = self.__add_sub_articles(d['entries'])
        return d

"""Code below extracts article from websites"""

class Barchart:
    def extract_html(self, url):
        driver = webdriver.Firefox()
        driver.maximize_window()
        try:
            driver.get(url)
        except:
            [0, ""]
        timer = random.uniform(5, 10)
        time.sleep(timer)
        try:
            alert = driver.find_element(By.XPATH, "//a[@id= 'alertBox']")
            alert = driver.switch_to.alert
            time.sleep(1)
            alert.dismiss()
        except Exception as e:
            print(e)
        try:
            ads = driver.find_element(By.XPATH, "//div[@id='dismiss-button']")
            time.sleep(1)
            ads.click()
        except Exception as e:
            print(e)
        
        html = driver.page_source
        driver.quit()
        return [1, html]
    
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_ = "ng-binding ng-scope").get_text()
        return article

class Benzinga:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        
        article = ""
        raw_article = soup.find_all(id = "article-body")
        for paragraph in raw_article:
            article += paragraph.get_text()
        av = AlphaVantage()
        article = av.remove_word("\xa0", article)
        return article

class Fast_Company:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article", class_ = "article-container").get_text()
        return article


class Forbes:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_= "body-container")
        return article.get_text()


class Forex_Live:
    def extract_article(self, html):
        
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article")
        return article.get_text()

class Fortune:
    def extract_article(self, html):
        
        soup = BeautifulSoup(html, "html.parser")
        article = ""
        paragraphs = soup.find_all("p")
        for paragraph in paragraphs:
            article += paragraph.get_text()
        return article

class FX_Street:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_= "fxs_article_content")
        return article.get_text()

class IBD:

    def extract_article(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find("single-post-content post-content drop-cap crawler")
        if article:
            return article.get_text()
        else:
            return ""
    
    def remove_word(self, text, word):

        """Takes in article string as input, removes all instances of \n from it"""

        article = re.sub(word, "", text)
        return article  
    

    def get_header(self, article_soup):
        author = article_soup[0].find(class_ = "authors-links")
        author = author.get_text()
        time = article_soup[0].find(class_ = "post-time")
        time = time.get_text()
        return author, time

    def get_videos(self, article_soup):

        videos = []
        for soup in article_soup:
            video = soup.find_all(class_ = "video-block-title")
            videos += video
        video_texts = []
        for video in videos:
            video_text = video.get_text()
            video_texts.append(video_text)

        for idx, vt in enumerate(video_texts):
            vt = remove_word(vt, "\n")
            video_texts[idx] = vt
        return video_texts


    def parse_article(self, html):
        
        soup = BeautifulSoup(html, 'html.parser')
        article_soup = soup.find_all("article")
        article_raw = ""
        for item in article_soup:
            article_raw += item.get_text()

        video_texts = self.get_videos(article_soup)
        author, time, title = self.get_header(article_soup)

        article_split = article_raw.split("\n")
        article = []
        for paragraph in article_split:
            if author in paragraph:
                continue

            if time in paragraph:
                continue

            if video_texts in paragraph:
                continue

            if paragraph == "":
                continue

            if "See All Videos" in paragraph:
                continue

            if "NOW PLAYING" in paragraph:
                continue

            if "YOU MAY ALSO LIKE" in paragraph:
                break
            article.append(paragraph+"\n")
        
        article = "\n".join(article)
        article = self.remove_word(article, "\xa0")
        return article


class Insider_Monkey:
    def extract_article(self, html):

        soup = BeautifulSoup(html, "html.parser")
        article = soup.find_all("div", class_ = "content-without-wrap single-content clearfix")
        article = article[0]
        return article.get_text()

class Investing:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", id = "article").get_text()
        return article

class Investment_News:
    def extract_html(self, html):
        driver = webdriver.Firefox()
        try:
            driver.get(url)
        except:
            return [0, ""]
        time.sleep(5)
        try:
            button = driver.find_element(By.XPATH, "//button[@class = 'pf-widget-close']")
            time.sleep(1)
            button.click()
        except Exception as e:
            print(e)
            pass
        
        html = driver.page_source
        driver.quit()
        return [1, html]
    
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_ = "article-detail__body")
        return article.get_text()

class Investopedia:
    def get_newstip(self, soup):
        news_tip = soup.find(class_ = "comp news-tip mntl-block")
        news_tip = news_tip.get_text()
        return news_tip.split("\n")
    
    def parse_article(self, html):

        soup = BeautifulSoup(html, "html.parser")
        raw_articles = soup.find_all(class_ = "loc article-content")
        if len(raw_articles) == 1:
            processed_article = raw_articles[0].get_text()
        else:
            processed_article = ""
            for article in raw_articles:
                processed_article += article.get_text()

        processed_article = processed_article.split("\n")
        news_tip = self.get_newstip(soup)
        
        parsed_article = []
        for paragraph in processed_article:

            if paragraph in news_tip:
                break
            if paragraph != "":
                parsed_article.append(paragraph+"\n")


        parsed_article = "\n".join(parsed_article)
        gn2 = Google()
        parsed_article = gn2.remove_word("TradingView", parsed_article)
        return parsed_article

class Markets:
    def extract_html(self, url):
        driver = webdriver.Firefox()
        driver.maximize_window()
        try:
            driver.get(url)
        except:
            return [0, ""]
        time.sleep(5)
        try:
            driver.find_element(By.XPATH, "//a[contains(text(), 'Accept')]").click()
        except Exception as e:
            print(e)
        html = driver.page_source
        driver.quit()
        return [1, html]
    
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = ""
        raw_articles = soup.find_all("div", class_ = "container-fluid")
        for raw in raw_articles:
            article += raw.get_text()
        return article

class Marketbeat:
    def extract_html(self, url):
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(5)
        
        #handle notification
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
            #webdriver wait until
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
        return [1, html]
    
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_= "body-copy lh-loose article-page")
        return article.get_text()    

class Market_Screener:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article").get_text()
        return article


class Money_Check:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = ""
        raw_article = soup.find_all("p")
        for result in raw_article:
            article += result.get_text()
            article += "\n"
        return article

class NASDAQ:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_nasdaq_article = soup.find_all(class_ = "body__content")
        nasdaq_article = ""
        for paragraph in raw_nasdaq_article:
            nasdaq_article += paragraph.get_text()
        return nasdaq_article

class Proactive_Investors:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_ = "ckeditor-content").get_text()
        return article

class Reuters:
    def extract_reuters(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article").get_text()
        return article

class Stock_Titan:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_ = "xn-content")
        return article.get_text()

class The_Street:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_= "m-detail--body").get_text()
        return article

class TipRanks:
    def extract_html(self, url):
        driver = webdriver.Firefox()
        driver.maximize_window()
        try:
            driver.get(url)
        except:
            return [0, ""]
        timer = random.uniform(5, 10)
        time.sleep(timer)
        try:
            button = driver.find_element(By.XPATH, "//span[contains(text(), 'Continue Reading')]")
            time.sleep(1)
            button.click()
        except Exception as e:
            print(e)
        html = driver.page_source
        driver.quit()
        return [1, html]
    
    def parse_article(self, html, ticker):
        soup = BeautifulSoup(html, "html.parser")
        raw_article = soup.find("article")
        processed_article = []
        paragraphs = raw_article.find_all("p")
        for paragraph in paragraphs:
            text = paragraph.get_text()
            if text in processed_article:
                continue
            processed_article.append(text)
        processed_article = "\n".join(processed_article)
        g = Google()
        parsed_article = g.remove_word(f"See more {ticker} analyst ratings\n", processed_article)
        return parsed_article

class Tokenist:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("div", class_ = "section-post__content text-wrap")
        return article.get_text()

class Trading_View:
    def extract_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article").get_text()
        return article

class WatcherGuru:
    def parse_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_article = soup.find("div", class_ = "entry-content")
        paragraphs = raw_article.find_all("p")
        parsed_article = ""
        for paragraph in paragraphs:
            paragraph = paragraph.get_text()+"\n"
            if "Also Read" in paragraph:
                continue
            parsed_article += paragraph
        return parsed_article

        
class WS_247:

    def get_tables(self, soup):
        table = soup.find_all("table")
        tables = []
        for item in table:
            item = item.get_text()
            item = item.split("\n")
            tables += item
        return tables

    def parse_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        raw_article = soup.find_all(class_ = "entry-content column content primary is-two-thirds")
        article = ""
        for paragraph in raw_article:
            article += paragraph.get_text()
        article = article.split("\n")
        tables = self.get_tables(soup)

        parsed_article = []
        for paragraph in article:
            if paragraph == "":
                continue
            if paragraph in tables:
                continue
            if "(Sponsored)" in paragraph:
                break
            parsed_article.append(paragraph+"\n")

        gn2 = Google()
        parsed_article = "\n".join(parsed_article)
        to_remove = ["\xa0", "Wikimedia Commons"]
        for word in to_remove:
            parsed_article = gn2.remove_word(word, parsed_article)
        return parsed_article
               