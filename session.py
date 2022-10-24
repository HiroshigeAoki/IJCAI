import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm
import os
import sys

cat = sys.argv[1]

# Proceedingsで、第一引数で指定したカテゴリーののsessionに属する論文のみ抽出。
if cat == 'nlp':
    year_num = [(2022, 9), (2021, 12), (2020, 11), (2019, 10), (2018, 9), (2017, 7)]
elif cat == 'xai':
    year_num = [(2022, 1), (2021, 1)]

for year, num in tqdm(year_num):
    res = requests.get(f'https://www.ijcai.org/proceedings/{year}/')
    soup = BeautifulSoup(res.content, features="html.parser")
    nlp = soup.find('div', {'id': f'subsection{num}'})
    papers = nlp.find_all('div', {'class': 'paper_wrapper'})
    titles, descs, tracks, categories, urls = [], [], [], [], []
    for paper in papers:
        href = paper.find('div', {'class': 'details'}).find_all('a')[1]['href']
        res = requests.get(f'https://www.ijcai.org{href}')
        url = res.url
        soup = BeautifulSoup(res.content, features="html.parser")
        title = soup.find('h1', {'class', 'page-title'}).text
        desc = re.sub(r'[\n\t\r]+', ' ', soup.find('div', {'class': 'col-md-12'}).text.strip())
        track = re.findall(r'(\w+) [tT]rack', soup.find_all('div', {'class': 'col-sm-12'})[1].text)[0]
        topics = soup.find_all('div', {'class': 'topic'})
        category = {}
        for topic in topics:
            mcat, *scat = map(lambda x: x.strip(), topic.text.split(': '))
            category.setdefault(mcat, []).append('_'.join(scat))

        titles.append(title)
        tracks.append(track)
        if cat == 'nlp':
            categories.append(category.get('Natural Language Processing', None))
        elif cat == 'xai':
            categories.append(category.get('AI Ethics, Trust, Fairness', None))
        urls.append(url)
        descs.append(desc)
        
    os.makedirs(f'./csv/{cat}/', exist_ok=True)
    pd.DataFrame(
        dict(
            title=titles,
            track=tracks,
            categories=categories,
            url=urls,
            desc=descs
        )
    ).to_csv(f'./csv/{cat}/{year}_main.csv')