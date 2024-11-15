"""
Operations for retrieving information from webpages
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_article(driver, link):
    """Get an article contents
    @driver: selenium driver
    @link: url to parse

    @returns dict with article keys
    """
    driver.get(link)

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
        print(e, "CRASHED READING CONSENT")

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
                    f"Button {index + 1} Text: {button.text} {cl} "
                )
            except Exception as e:
                print(e, "CRASH")

        try:
            link = driver.find_element(By.CLASS_NAME, "readmoreButtonText")
            if link:
                link.click()
        except Exception as e:
            print(" NO READ MORE BUTTON ")

    except Exception as e:
        print(e, "CRASHED")

    print("AFTER READ MORE")

    try:
        article = driver.find_element(By.TAG_NAME, "article")
        article = article.text

    except:
        print("article tag not found")
        article = ""
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for paragraph in paragraphs:
            article += paragraph.text

    print("ARTICLE PARSED")

    return article