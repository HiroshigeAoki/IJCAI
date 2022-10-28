import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm
import os
import joblib
import sys

os.makedirs('./csv/nlp', exist_ok=True)

# IJCAIのProceedingsの論文から、第一引数で指定されたカテゴリ(nlp, xai, planning)の論文の「タイトル」、「トラック」、「カテゴリ」、「URL」、「概要」を取得する。
# 実行時間：約8分程度。

years = [2022, 2021, 2020, 2019, 2018, 2017]
cat = sys.argv[1]

def extract(year):
    res = requests.get(f'https://www.ijcai.org/proceedings/{year}/')
    soup = BeautifulSoup(res.content, features="html.parser")
    details = soup.find_all('div', {'class': 'details'})
    titles, descs, tracks, categories, urls = [], [], [], [], []
    for detail in tqdm(details, desc=f'{year}'):
        href = detail.find_all('a')[1]['href']
        res = requests.get(f'https://www.ijcai.org{href}')
        url = res.url
        soup = BeautifulSoup(res.content, features="html.parser")
        title = soup.find('h1', {'class', 'page-title'}).text
        desc = re.sub(r'[\n\t\r]+', ' ', soup.find('div', {'class': 'col-md-12'}).text.strip())
        try:
            track = re.findall(r'(\w+) [tT]rack', soup.find_all('div', {'class': 'col-sm-12'})[1].text)[0]
        except IndexError:
            track = re.findall(r'([\w ]+)\. Pages', soup.find_all('div', {'class': 'col-sm-12'})[1].text)[0]
        topics = soup.find_all('div', {'class': 'topic'})
        category = {}
        for topic in topics:
            mcat, *scat = map(lambda x: x.strip(), topic.text.split(': '))
            category.setdefault(mcat, []).append('_'.join(scat))
        if cat == 'nlp':
            category = category.get('Natural Language Processing', None)
        elif cat == 'xai':
            category = category.get('AI Ethics, Trust, Fairness', None)
            if category is None:
                category = category.get('AI Ethics', None)
        elif cat == 'planning':
            category = category.get('Planning and Scheduling', None)
            
                
        if category is not None:
            titles.append(title)
            descs.append(desc)
            tracks.append(track)
            categories.append(category)
            urls.append(url)
    
    os.makedirs(f'./csv/{cat}', exist_ok=True)
    pd.DataFrame(
        dict(
            title=titles,
            track=tracks,
            categories=categories,
            url=urls,
            desc=descs        
        )
    ).to_csv(f'./csv/{cat}/{year}.csv')


def main():
    joblib.Parallel(n_jobs=len(years), backend="threading")(
        joblib.delayed(extract)(
            year,
        ) for year in years
    )

if __name__ == "__main__":
    main()
