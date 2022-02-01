import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import numpy as np
from time import sleep
import requests
from tqdm import tqdm
import time
import random
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def get_issues_and_covers(page_data):
    
    covers = []
    issues_link = []
    issues_nr = []
    # get covers
    spans = page_data.find_all('span') 
    for span in spans:
        class_ = span.get('class')

        if class_ is None:
            continue

        elif class_[0] == 'image_approved':
            covers.append(span.find('a').get('href'))

        else:
            covers.append('no_cover')
    # get issues
    tds = page_data.find_all('td', class_='issue')        
    for td in tds:
        a = td.find_all('a')[-1]
        ref = a.get('href')
        txt = a.text
        issues_link.append(ref)
        issues_nr.append(txt)
    
    return issues_link, issues_nr, covers

def all_issues_scraper(browser, link):

    browser.get(link)
    # WebDriverWait(browser, wait_time).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'page_1')))
    time.sleep(1 + random.random()) 
    try:
        # click on accept cookies and privacy aggreements
        browser.find_elements_by_xpath("//button[@class=' css-47sehv']")[0].click()
        time.sleep(2) # wait a bit for the page to load
        browser.find_elements_by_xpath("//a[@class='cc_btn cc_btn_accept_all']")[0].click()
        time.sleep(2) # wait a bit for the page to load
    except IndexError:
        pass
    

    soup_file = browser.page_source
    soup = BeautifulSoup(soup_file, 'html.parser')
    # get 1st page of issues which is automatically loaded
    page_data = soup.find('form', id='current_comics').find('div', class_='page_1')
    issues_link, issues_nr, covers = get_issues_and_covers(page_data) # get all issues and cover links from page 1


    
    # get all pages that are not diplayed and should be clicked upon if they exist
    pages = browser.find_elements_by_xpath("//a[@class='g']")
    
    if pages != []:

        for i, page in zip(range(2, len(pages) + 2), pages):    
            # print(f'clicked on page_{i}')
            page.click()

            # WebDriverWait(browser, wait_time).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, f'page_{i}')))
            time.sleep(2.5)
            soup_file = browser.page_source
            soup = BeautifulSoup(soup_file, 'html.parser')
            page_data = soup.find('form', id='current_comics').find('div', class_=f'page_{i}')
            # print(issues)
            data = get_issues_and_covers(page_data)
            issues_link.extend(data[0])
            issues_nr.extend(data[1])
            covers.extend(data[2])
        
    df = pd.DataFrame({
          'issue_link': issues_link,
          'issue_nr': issues_nr,
          'cover_link': covers,
        
        })
    
    if df.empty:
        df = df.append([np.nan], ignore_index=True).drop(0, axis=1)

    return df

        
def start_chrome(headless=True, driver_path='./'):
    # use selenium webdriver so we can scrape the javascript elements
    # chromedriver should be in the path or it should be provided. version should correspond to the chrome version installed
    # Link for versions: https://chromedriver.chromium.org/downloads
    if headless:
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument('--blink-settings=imagesEnabled=false')
        opts.add_argument(" --headless")
        chrome_driver = "chromedriver"# Instantiate a webdriver
        browser = webdriver.Chrome(options=opts, executable_path=driver_path+chrome_driver)# Load the HTML page
    else:
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument('--blink-settings=imagesEnabled=false')
        chrome_driver = "chromedriver"
        browser = webdriver.Chrome(options=opts, executable_path=driver_path+chrome_driver)

    
    return browser

df1 = pd.read_csv('titles_list_data.csv', index_col=0, low_memory=False)
df1 = df1[df1.issues != '0']

browser = start_chrome(headless=True)

site_link = 'https://comicbookrealm.com'
frames_list = []
df1 = df1.iloc[:17000]

iterates = tqdm(zip(range(df1.shape[0]), df1.pub_id, df1.pub_name, df1.title, df1.title_link))

for i, pub_id, pub_name, title, link in iterates:
    
    
    iterates.set_description(f"Processing: {title} ({pub_name}) - {i + 1} out of {df1.shape[0]}")
    try:
        frame = all_issues_scraper(browser, site_link+link)
    except:
        try:
            time.sleep(1)
            frame = all_issues_scraper(browser, site_link+link)
        except:
            continue
    frame.insert(0, 'title_link', link)
    frame.insert(0, 'title', title)
    frame.insert(0, 'pub_id', pub_id)
    frames_list.append(frame)
    if i%1000 == 0 and i > 0:
        temp = pd.concat(frames_list, axis=0)
        temp.to_csv(f'./backup_data/issues_data_{i}.csv')
    
df = pd.concat(frames_list, axis=0)
df.to_csv('issues_data_part1.csv')
browser.quit()