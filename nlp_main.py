import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm
import os

os.makedirs('./csv/nlp', exist_ok=True)

# ProceedingsでMain TrackでNatural Language Processingのところだけ取ったもの。

year_num = [(2022, 9), (2021, 12), (2020, 11), (2019, 10), (2018, 9), (2017, 7)]
for year, num in tqdm(year_num):
    res = requests.get(f'https://www.ijcai.org/proceedings/{year}/')
    soup = BeautifulSoup(res.content, features="html.parser")
    nlp = soup.find('div', {'id': f'subsection{num}'})
    papers = nlp.find_all('div', {'class': 'paper_wrapper'})
    titles, tracks, categories, urls = [], [], [], []
    for paper in papers:
        href = paper.find('div', {'class': 'details'}).find_all('a')[1]['href']
        res = requests.get(f'https://www.ijcai.org{href}')
        url = res.url
        soup = BeautifulSoup(res.content, features="html.parser")
        title = soup.find('h1', {'class', 'page-title'}).text
        track = re.findall(r'(\w+) [tT]rack', soup.find_all('div', {'class': 'col-sm-12'})[1].text)[0]
        topics = soup.find_all('div', {'class': 'topic'})
        category = {}
        for topic in topics:
            mcat, *scat = map(lambda x: x.strip(), topic.text.split(': '))
            category.setdefault(mcat, []).append('_'.join(scat))

        titles.append(title)
        tracks.append(track)
        categories.append(category.get('Natural Language Processing', None))
        urls.append(url)
        
    pd.DataFrame(
        dict(
            title=titles,
            track=tracks,
            categories=categories,
            url=urls,            
        )
    ).to_csv(f'./csv/nlp/{year}_main.csv')