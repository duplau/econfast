import json, os, argparse, time, sys, requests, urllib3
from urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

'''
Ce fichier est un utilitaire de scraping de résultats de Google Image Search.
Il a été conçu dans le cadre spécifique du hackathon et ne se veut pas un outil générique.
'''

urllib3.disable_warnings(InsecureRequestWarning)

def create_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    try:
        browser = webdriver.Chrome("/Applications/chromedriver", options=options)
    except Exception as e:
        print(f'No found chromedriver in this environment.')
        print(f'Install on your machine. exception: {e}')
        sys.exit()
    browser.set_window_size(1280, 1024)
    return browser

def yield_image_urls(browser, phrases, pages_down=0, max_images=3):
    search_url = 'https://www.google.com/search?q=' + '+'.join(phrases) + '&source=lnms&tbm=isch&num=3'
    browser.get(search_url)
    time.sleep(1)
    element = browser.find_element_by_tag_name('body')
    if pages_down > 0:
        try:
            browser.find_element_by_id('smb').click()
            for i in range(pages_down):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
        except Exception as e:
            print('Could not scroll down', e)
    page_source = browser.page_source 
    soup = BeautifulSoup(page_source, 'lxml')
    images = soup.find_all('img')
    count = 0
    for image in images:
        try:
            url = image['data-src']
            yield url
            count += 1
            if count >= max_images:
                return
        except:
            try:
                url = image['src']
                yield url
                count += 1
                if count >= max_images:
                    return
            except Exception as e:
                print('No image source found', e)

def destroy_browser(browser):
    browser.close()
