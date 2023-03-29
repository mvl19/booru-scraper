from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import requests
from random import randint, random
import time
from datetime import datetime

"""
TODO: add argparse functionality
"""
logging.basicConfig(level=logging.DEBUG, format=('%(asctime)s - %(levelname)s - %(message)s'))
logging.debug('Start...')


def generate_filename(term):
    current_time = datetime.now().strftime('Y%m%d%H%S%M')
    stem = '_'.join(term.split(' '))
    filename = stem + ' ' + current_time + '.jpg'
    return filename


def sleep_for_random_interval() -> None:
    seconds = random() * 2
    time.sleep(seconds)


def initialize(path) -> webdriver.Firefox:
    wb = webdriver.Firefox(executable_path=path)
    return wb


def load(driver: webdriver.Firefox, url) -> webdriver.Firefox:
    try:
        driver.get(url)
        return driver
    except Exception as e:
        print(f'Exception {e} was encountered.')


def next_page(driver: webdriver.Firefox):
    next = driver.find_element(By.XPATH, '//a[@alt="next"]')
    return next


def download_image(hrefs: list[str], path, term) -> None:
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
    }
    for href in hrefs:
        try:
            res = requests.get(href.get_attribute('href'), headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            source = soup.find('img', {'id': 'image'})
            r = requests.get(source['src'])
            r.raise_for_status()
            with open(path + generate_filename(term), 'wb') as img:
                for chunk in r.iter_content(100000):
                    img.write(chunk)
        except Exception as e:
            print(f'Exception {e} encountered.')


def main(text: str, path) -> None:
    page = 0
    while True:
        page += 1
        if page == 1:
            WebDriverWait(driver, timeout=15).until(
                EC.presence_of_element_located((By.XPATH, '//div/input[@id="tags"]')))
            elem = driver.find_element(By.XPATH, '//div/input[@id="tags"]')
            for char in text:
                time.sleep(randint(1, 2))
                elem.send_keys(char)
            WebDriverWait(driver, timeout=15).until(EC.presence_of_element_located((By.XPATH, '//li[@aria-selected'
                                                                                              '="false"]')))
            real_search = driver.find_element(By.XPATH, '//li[@aria-selected="false"]').text
            real_search = real_search.split(' ')[0]
            driver.find_element(By.XPATH, '//div/input[@id="tags"]').clear()
            driver.find_element(By.XPATH, '//div/input[@id="tags"]').send_keys(real_search)
            driver.find_element(By.XPATH, '//input[@name="searchDefault"]').send_keys(Keys.RETURN)
            WebDriverWait(driver, timeout=15).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="content"]/div'
                                                          '/span/a')))
            hrefs = driver.find_elements(By.XPATH, '//div[@class="content"]/div/span/a')
            # print('\n',page, hrefs)
            download_image(hrefs, path=path, term=text)
        else:
            WebDriverWait(driver, timeout=15).until(
                EC.presence_of_element_located((By.XPATH, '//a[@alt="next"]'))).click()
            WebDriverWait(driver, timeout=15).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="content"]/div'
                                                          '/span/a')))
            hrefs = driver.find_elements(By.XPATH, '//div[@class="content"]/div/span/a')
            # print('\n',page, hrefs)
            download_image(hrefs, path=path, term=text)


if __name__ == "__main__":
    driver = initialize()
    driver = load(driver=driver, url='https://safebooru.org/')
    main("saber")
    print('Completed Execution successfully.')
