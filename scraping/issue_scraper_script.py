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
import re

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

def issue_scraper(browser, issue_link, issue_nr, cover_link, title, title_link, sleep_time=0.8):
    
    data_dict = {'title': title, 
                 'title_link': title_link, 
                 'issue_link': issue_link,
                 'cover_link': cover_link}
    
    browser.get(issue_link)
    # WebDriverWait(browser, wait_time).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'page_1')))
    time.sleep(sleep_time + random.random())
    try:
        # click on accept cookies and privacy aggreements
        browser.find_elements_by_xpath("//button[@class=' css-47sehv']")[0].click()
        time.sleep(1) # wait a bit for the page to load
        browser.find_elements_by_xpath("//a[@class='cc_btn cc_btn_accept_all']")[0].click()
        time.sleep(1) # wait a bit for the page to load
    except IndexError:
        pass
    
    soup_file = browser.page_source
    soup = BeautifulSoup(soup_file, 'html.parser')
    issue_data = (soup.find('div', id='comic-details-content')
                     .find('table', class_='auto-table')
                     .find_all('td', class_='data')
                 )
    issue_labels = (soup.find('div', id='comic-details-content')
                        .find('table', class_='auto-table')
                        .find_all('td', class_='label')
                   )
    labels = ['issue', 'cover_date', 'cover_price', 'current_value',
        'searched', 'owned', 'pages', 'rating', 'ISBN-UPC', 
       'est_print_run', 'variant_of', 'preview']

    for dat, label, lab in zip(issue_data, issue_labels, labels):
        data_dict[lab] = dat.text.strip()
        if label.text == 'Current Value:':
            data_dict['hist_prices_link'] = dat.find('a').get('href')
        if dat.find('img') is not None and label.text == 'Rating:':
            rating = dat.find('img').get('title')
            rating = re.findall("\d+\.\d+|\d+", rating)
            data_dict['rating'] = float(rating[0])
            data_dict['rating_count'] = int(rating[1])
            
    data_dict['synopsis'] = soup.find('div', id='synopsis').text.strip()
    # get info from contributors tab
    browser.find_elements_by_xpath("//li[@ref='contributors']")[0].click()
    time.sleep(sleep_time)
    
    soup_file = browser.page_source
    soup = BeautifulSoup(soup_file, 'html.parser')
    creators = soup.find('div', id='contributors').find_all('li')
    
    if len(creators) == 1 and creators[0].text == 'There have been no contributors assigned to this issue':
        names = 'no contributors assigned'
        jobs = 'no contributors assigned'
    else:
        names = []
        jobs = []
        for li in creators:
            contrib = li.text.strip()
            names.append(contrib.split('\n', 1)[0])
            j = contrib.split('\n', 1)[1]
            jobs.append(re.sub('\s*', '', j))

    
    data_dict['contributors_names'] = str(names)
    data_dict['contributors_roles'] = str(jobs)
    
    # get info from characters tab
    browser.find_elements_by_xpath("//li[@ref='characters']")[0].click()
    time.sleep(sleep_time)
    
    soup_file = browser.page_source
    soup = BeautifulSoup(soup_file, 'html.parser')
    
    characters = soup.find('div', id='characters').find_all('li')
    
    if len(characters) == 1 and characters[0].text == 'There have been no characters assigned to this issue':
        character_data = 'no characters assigned'
    
    else:
        character_data = []
        for li in characters:
            name = li.find('a').text.strip()
            photo_link = li.find('img').get('src')
            extra_info = li.find('span').text.strip()
            if '(' not in extra_info:
                extra_info = ''

            event = li.find('span', class_='d').text.strip()
            character_data.append([name, photo_link, extra_info, event])
    
    data_dict['characters'] = str(character_data)
    
    return pd.DataFrame(data_dict, index=[0])
    
    

df = pd.read_csv('all_issues_data.csv', index_col=0)

browser = start_chrome(headless=True)

site_link = 'https://comicbookrealm.com'
sleep_time = 1
df1 = df.iloc[345000:]

iterates = tqdm(zip(range(df1.shape[0]), 
                    df1.issue_link, 
                    df1.issue_nr, 
                    df1.cover_link, 
                    df1.title,
                    df1.title_link,
                   )
               )

frames_list = []

for i, issue_link, issue_nr, cover_link, title, title_link in iterates:
    
    iterates.set_description(f"Processing: {title}: {issue_nr} - {i + 1+345000} / {df1.shape[0]+345000}")
    
    try:
        frame = issue_scraper(browser, site_link+issue_link, issue_nr, cover_link, title, title_link, sleep_time)
    
    except AttributeError:
        time.sleep(2)
        try:
            frame = issue_scraper(browser, site_link+issue_link, issue_nr, cover_link, title, title_link, sleep_time)
        except AttributeError:
            continue
    
        
    
    frames_list.append(frame)
    
    if i%10000 == 0 and i > 0:
        temp = pd.concat(frames_list, axis=0)
        temp.to_csv(f'./backup_data/single_issue_data_{i+345000}.csv')

browser.quit()

dff = pd.concat(frames_list, axis=0).reset_index(drop=True)
dff.to_csv('single_issue_data_part4.csv')