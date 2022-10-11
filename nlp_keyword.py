import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm
import os
import joblib

os.makedirs('./csv/nlp', exist_ok=True)

# Proceedingsの論文でKeywordに"Natural Language Processing"を含むもの。

years = [2022, 2021, 2020, 2019, 2018, 2017]

def extract_nlp(year):
    res = requests.get(f'https://www.ijcai.org/proceedings/{year}/')
    soup = BeautifulSoup(res.content, features="html.parser")
    details = soup.find_all('div', {'class': 'details'})
    titles, tracks, categories, urls = [], [], [], []
    for detail in tqdm(details, desc=f'{year}'):
        href = detail.find_all('a')[1]['href']
        res = requests.get(f'https://www.ijcai.org{href}')
        url = res.url
        soup = BeautifulSoup(res.content, features="html.parser")
        title = soup.find('h1', {'class', 'page-title'}).text
        try:
            track = re.findall(r'(\w+) [tT]rack', soup.find_all('div', {'class': 'col-sm-12'})[1].text)[0]
        except IndexError:
            track = re.findall(r'([\w ]+)\. Pages', soup.find_all('div', {'class': 'col-sm-12'})[1].text)[0]
        topics = soup.find_all('div', {'class': 'topic'})
        category = {}
        for topic in topics:
            mcat, *scat = map(lambda x: x.strip(), topic.text.split(': '))
            category.setdefault(mcat, []).append('_'.join(scat))
        
        nlp_category = category.get('Natural Language Processing', None)
        if nlp_category is not None:
            titles.append(title)
            tracks.append(track)
            categories.append(nlp_category)
            urls.append(url)
        
    pd.DataFrame(
        dict(
            title=titles,
            track=tracks,
            categories=categories,
            url=urls,            
        )
    ).to_csv(f'./csv/nlp/{year}.csv')


def main():
    joblib.Parallel(n_jobs=len(years), backend="threading")(
        joblib.delayed(extract_nlp)(
            year,
        ) for year in years
    )

if __name__ == "__main__":
    main()
