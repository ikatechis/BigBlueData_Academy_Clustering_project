import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from time import sleep
import requests
from tqdm import tqdm
import time
import random
from fake_useragent import UserAgent
import sys

def get_hist_values(link, sleep_time=0.6, random_sleep=True, random_agent=True):
    main_link = 'https://comicbookrealm.com' + link
    if random_agent:
        ua = UserAgent()
        headers = {'User-agent': f'{ua.random}'}
        
    else:
        headers = {'User-agent': ''}
        
    response = requests.get(main_link, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    dates = [td.text.strip() for td in soup.find_all('td', class_='item')]
    prices = [td.text.strip() for td in soup.find_all('td', class_='data')]
    
    frame = pd.DataFrame({'hist_prices_link': link, 'dates': str(dates), 
                          'prices': str(prices)}, index=[0])
    
    sleep(sleep_time + np.random.random()/2*random_sleep)
    
    return frame

def hist_scraper(data_path, data_range=(0, 10), sleep_time=0.6, random_sleep=True, random_agent=True):
    df = pd.read_parquet(data_path).iloc[data_range[0]: data_range[1]]
    frames = []
    iterator = tqdm(enumerate(df.hist_prices_link))
    
    for i, link in iterator:
        if link is not None:
            iterator.set_description(f"Processing: {i + 1 + data_range[0]} / {df.shape[0] + data_range[0]}")
            frame = get_hist_values(link, sleep_time, random_sleep, random_agent)
            frames.append(frame)
        else:
            continue
                                     
        if i%10000 == 0 and i > 0:
            temp = pd.concat(frames, axis=0)
            temp.to_csv(f'backup_data/hist_prices_data_{i + data_range[0]}.csv', index=False)
                                     
                            
    df_hist = pd.concat(frames, axis=0).reset_index(drop=True)
    df_hist.to_csv('hist_prices_data.csv', index=False)
    
    return df_hist

if __name__ == '__main__':
    
    start = int(float(sys.argv[1]))
    stop = int(float(sys.argv[2]))
    sleep_time = float(sys.argv[3])
    hist_scraper('all_data.parquet', data_range=(start, stop), sleep_time=sleep_time)