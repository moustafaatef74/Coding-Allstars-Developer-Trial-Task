import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import langdetect
import csv
import random
import time
from urllib.request import urlopen
from PIL import Image


def readCSV()-> list:
    with open("data.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader) # skip the first line
        values = [row[0] for row in reader]
        random_values = random.sample(values, 5)
        return random_values

def createDriver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.headless = True


    chrome_options.add_experimental_option("prefs", prefs)
    myDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return myDriver

def isHindi(text: str) -> bool:
    try:
        return langdetect.detect(text) == 'hi'
    except:
        return False

def checkWebsites() -> dict:
    websites = readCSV()
    results = {}
    driver = webdriver.Chrome()
    for website in websites:
        try:
            driver.get(website)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = driver.page_source
            if "classcentral" not in page_source:
                results[website] = "Wrong page"
                continue
            soup = BeautifulSoup(page_source, 'html.parser')
            hindi_found = False
            for text_elem in soup.find_all(string=True):
                if text_elem.parent.name in ['style', 'script', 'head', 'title']:
                    continue
                if text_elem.strip().startswith('::'):
                    continue
                if isHindi(text_elem.strip()):
                    hindi_found = True
                    break
            if hindi_found:
                results[website] = "PASS"

                # Hover on the button with class="hidden weight-semi large-up-block text-1 color-charcoal padding-right-small"
                button = driver.find_element(By.CLASS_NAME, "hidden.weight-semi.large-up-block.text-1.color-charcoal.padding-right-small")
                hover = ActionChains(driver).move_to_element(button)
                hover.perform()

                # Check if class="sticky-footer" changed to class="sticky-footer nav-open"
                try:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sticky-footer.nav-open")))
                except:
                    results[website] += ", Javascript dropdown not working properly"

                # Check image size of img element with alt="Never stop learning."
                img = driver.find_element(By.XPATH, "//img[@alt='Never stop learning.']")
                img_src = img.get_attribute("src")
                with urlopen(img_src) as url:
                    img_file = Image.open(url)
                    img_size = len(img_file.fp.read())
                    if img_size < 50000:
                        results[website] += ", Images not high resolution"
                    else:
                        pass

                hrefs = []
                for link in driver.find_elements(By.TAG_NAME, 'a'):
                    href = link.get_attribute('href')
                    if href is not None:
                        if "http" not in href:
                            href = website + href
                        hrefs.append(href)
                if len(hrefs) > 0:
                    sample_size = min(len(hrefs), 5)
                    for link in random.sample(hrefs, sample_size):
                        try:
                            driver.get(link)
                            wait = WebDriverWait(driver, 20)
                            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                            page_source = driver.page_source
                            soup = BeautifulSoup(page_source, 'html.parser')
                            hindi_found = False
                            for text_elem in soup.find_all(string=True):
                                if text_elem.parent.name in ['style', 'script', 'head', 'title']:
                                    continue
                                if text_elem.strip().startswith('::'):
                                    continue
                                if isHindi(text_elem.strip()):
                                    hindi_found = True
                                    break
                            if hindi_found:
                                continue
                            else:
                                results[website] += ", Inner pages not translated"
                                break
                        except Exception as e:
                            pass
            else:
                results[website] = "Not Translated"
        except Exception as e:
            results[website] = "FAIL"
    driver.quit()
    return results


