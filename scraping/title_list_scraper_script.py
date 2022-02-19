import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook as tqdm
from datetime import datetime
import numpy as np
from time import sleep
import requests
from tqdm import tqdm
import time
import random
from fake_useragent import UserAgent

def comic_list_scraper(pub_id, pub_name, letter, link, fake_agent=True):
    if fake_agent:
        ua = UserAgent()
        headers = {'User-agent': f'{ua.random}'}
    else:
        headers = {'User-agent': ''}
    
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    titles_lst = soup.find_all('td', class_='title')
    titles_lst = [td.find('a') for td in titles_lst]
    
    titles_links = [a['href'] for a in titles_lst if a['href'] is not None]
    titles = [a.text.strip() for a in titles_lst]
    volume = [td.text.strip() for td in soup.find_all('td', class_='volume')]
    years = [td.text.strip() for td in soup.find_all('td', class_='years')]
    issues = [td.text.strip() for td in soup.find_all('td', class_='issues data-column')]
    
    df = pd.DataFrame({
                        'pub_id': [pub_id]*len(titles),
                        'pub_name': [pub_name]*len(titles),
                        'letter': [letter]*len(titles),
                        'title': titles,
                        'title_link': titles_links,
                        'volume': volume,
                        'years': years,
                        'issues': issues,
        
                        })
    return df

pubs = pd.read_csv('publishers_data.csv', index_col=0)

site_link = 'https://comicbookrealm.com'
titles_data = []
# pubs = pubs.iloc[1090:, :]
iterates = tqdm(zip(range(len(pubs.id)), pubs.id, pubs.name, pubs.titles_AZ.apply(eval)))
for i, id, name, titles in iterates:
    iterates.set_description(f"Processing: {name} - {i + 1} out of {pubs.shape[0]}")

    for title in titles:
        letter = title[-1]
        link = site_link + title[0]
        try:
            dat = comic_list_scraper(id, name, letter, link, fake_agent=False)
        except:
            time.sleep(1)
            try:
                dat = comic_list_scraper(id, name, letter, link, fake_agent=False)
            except:
                continue
        titles_data.append(dat)
        time.sleep(0.2 + random.random())
        
    if i%1000 == 0 and i > 0:
        temp = pd.concat(titles_data, axis=0)
        temp.to_csv(f'titles_list_{i}.csv')
        
df_titles = pd.concat(titles_data).reset_index(drop=True)
df_titles.to_csv('titles_list_data.csv')
print('Job Done!')
